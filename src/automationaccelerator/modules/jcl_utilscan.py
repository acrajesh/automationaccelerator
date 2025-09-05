import os
import re
import yaml
import pandas as pd
import threading
from queue import Queue
from datetime import datetime
import xlsxwriter
import math
import sys
import logging

# Queue for multi-threaded file processing
file_queue = Queue()
extracted_data = []
lock = threading.Lock()

def load_config(yaml_file):
    """ Load configuration from YAML file """
    if not os.path.exists(yaml_file):
        print("Configuration file not found! Exiting.")
        exit(1)
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def add_output_dir_to_config(config, output_dir):
    """ Add output directory to configuration """
    if 'output' not in config:
        config['output'] = {}
    config['output']['directory'] = output_dir
    return config

def validate_directory(path):
    """ Validate if a directory exists, re-prompt if invalid """
    while not os.path.isdir(path):
        path = input(f"Invalid directory: {path}. Please enter a valid path: ").strip()
    return path

def generate_versioned_filename(base_filename):
    """ Generate a versioned filename if a file already exists """
    if not os.path.exists(base_filename):
        return base_filename

    version = 1
    file_root, file_ext = os.path.splitext(base_filename)
    while os.path.exists(f"{file_root}_v{version}{file_ext}"):
        version += 1
    return f"{file_root}_v{version}{file_ext}"

def resolve_symbolic_parameter(param_name, jcl_content, proc_libraries, cntllib_path):
    """
    Resolve symbolic parameters by searching for their definitions
    
    Args:
        param_name (str): The parameter name without the & prefix
        jcl_content (list): List of lines from the JCL file
        proc_libraries (list): List of paths to PROC libraries
        cntllib_path (str): Path to the CNTLLIB directory
        
    Returns:
        str: The resolved parameter value or None if not found
    """
    # First check for SET statements in the JCL
    for line in jcl_content:
        set_match = re.match(r"//\s+SET\s+(\w+)=(.+)", line, re.IGNORECASE)
        if set_match and set_match.group(1).upper() == param_name.upper():
            return set_match.group(2).strip()
    
    # Check for parameter in JCL EXEC statement with PROC
    for i, line in enumerate(jcl_content):
        # Look for EXEC statements with PROC
        proc_match = re.match(r"//\S+\s+EXEC\s+(\w+)", line, re.IGNORECASE)
        if proc_match:
            proc_name = proc_match.group(1)
            # Look for parameter override in the EXEC statement
            param_pattern = rf"\b{param_name}\s*=\s*([^,\s]+)"
            param_match = re.search(param_pattern, line, re.IGNORECASE)
            if param_match:
                return param_match.group(1)
            
            # If not found in override, look in the PROC definition
            proc_content = find_proc_content(proc_name, proc_libraries)
            if proc_content:
                # Extract default parameter value from PROC definition
                for proc_line in proc_content:
                    # Look for PROC statement with parameter definition
                    proc_def_match = re.search(rf"//\S+\s+PROC\b.*\b{param_name}\s*=\s*([^,\s]+)", proc_line, re.IGNORECASE)
                    if proc_def_match:
                        return proc_def_match.group(1)
    
    # Check for symbolic parameter in INCLUDE statements
    for i, line in enumerate(jcl_content):
        include_match = re.search(r"//\s*INCLUDE\s+MEMBER\s*=\s*(\w+)", line, re.IGNORECASE)
        if include_match:
            member_name = include_match.group(1)
            # Look for the member in CNTLLIB
            if cntllib_path:
                member_path = os.path.join(cntllib_path, f"{member_name}.incl")
                if os.path.exists(member_path):
                    with open(member_path, 'r') as f:
                        member_content = f.readlines()
                        # Search for parameter in member content
                        for member_line in member_content:
                            param_match = re.search(rf"\b{param_name}\s*=\s*([^,\s]+)", member_line, re.IGNORECASE)
                            if param_match:
                                return param_match.group(1)
    
    # If still not found, check CNTLLIB for member with parameter name
    if cntllib_path:
        # Try direct member match
        member_path = os.path.join(cntllib_path, f"{param_name}.incl")
        if os.path.exists(member_path):
            with open(member_path, 'r') as f:
                return f.read().strip()
        
        # Try searching all CNTLLIB members for parameter definition
        for root, _, files in os.walk(cntllib_path):
            for file in files:
                if file.endswith('.incl'):
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            for line in f:
                                param_match = re.search(rf"\b{param_name}\s*=\s*([^,\s]+)", line, re.IGNORECASE)
                                if param_match:
                                    return param_match.group(1)
                    except Exception:
                        # Skip files that can't be read
                        continue
    
    # Parameter not found
    return None

def find_proc_content(proc_name, proc_libraries):
    """
    Find and read the content of a PROC from the available PROC libraries
    
    Args:
        proc_name (str): Name of the PROC to find
        proc_libraries (list): List of paths to PROC libraries
        
    Returns:
        list: Lines of the PROC content or None if not found
    """
    for proc_lib in proc_libraries:
        proc_path = os.path.join(proc_lib, f"{proc_name}.proc")
        if os.path.exists(proc_path):
            with open(proc_path, 'r') as f:
                return f.readlines()
    return None

def extract_steps_from_file():
    """ Worker function for multi-threaded file processing """
    while not file_queue.empty():
        file_path, utilities, file_type, cntllib_path, proc_libraries = file_queue.get()
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
                if not lines:
                    log_error(f"Empty file: {file_path}")
                    continue  # Skip empty files
                
                # Store the entire file content for parameter resolution
                jcl_content = lines
                
                # proc_libraries is now passed directly to the worker thread
                
                last_step_end = 0  # Track the end of the last step
                
                for i, line in enumerate(lines):
                    if re.match(r"//\*\s*EXEC", line, re.IGNORECASE):
                        continue

                    # Updated regex to capture symbolic parameters (e.g., &UTILITY)
                    match = re.match(r"//(\S+)\s+EXEC\s+(?:PGM\s*=\s*)?(\b\w+\b|&\w+)", line, re.IGNORECASE)
                    if match:
                        step_name = match.group(1)
                        program_name = match.group(2).upper()
                        
                        # Handle symbolic parameters
                        if program_name.startswith('&'):
                            param_name = program_name[1:]  # Remove & prefix
                            resolved_name = resolve_symbolic_parameter(param_name, jcl_content, proc_libraries, cntllib_path)
                            if resolved_name:
                                program_name = resolved_name.upper()
                                # Only log unresolved parameters to reduce log clutter
                            else:
                                # Skip this step if parameter couldn't be resolved
                                log_error(f"Unresolved symbolic parameter {program_name} in {os.path.basename(file_path)}")
                                continue
                        
                        if program_name in utilities:
                            
                            # Capture preceding comments separately
                            comment_block = []
                            step_block = []
                            j = i - 1
                            while j >= last_step_end:
                                if (
                                    lines[j].strip() == "" or
                                    re.match(r"//\S+\s+EXEC\s+PGM=", lines[j], re.IGNORECASE)
                                ):
                                    break
                                if lines[j].startswith("//*"):
                                    comment_block.insert(0, lines[j].strip())  # Maintain order
                                j -= 1

                            # Add the EXEC step and all associated DD statements
                            step_block.append(line.strip())
                            j = i + 1
                            while j < len(lines) and not re.match(r"//\S+\s+EXEC\s+PGM=", lines[j], re.IGNORECASE):
                                if lines[j].strip() == "":
                                    break
                                if lines[j].startswith("//"):
                                    step_block.append(lines[j].strip())
                                j += 1

                            # Capture SYSIN statement
                            sysin_type = "None"
                            sysin_statement = ""
                            control_card_member = ""
                            control_card_content = ""

                            for step_line in step_block:
                                if re.search(r"//\s*SYSIN\s+DD\s+\*", step_line):  # Handles variations like "// SYSIN DD *"
                                    sysin_type = "Inline SYSIN"
                                    sysin_statement = step_line.strip()  # Capture only the first line
                                    break

                                elif re.search(r"//\s*SYSIN\s+DD\s+DSN=", step_line):  # Control-card SYSIN
                                    sysin_type = "Control Card"
                                    m = re.search(r"DSN=[^,]+\(([^)]+)\)", step_line)
                                    if m:
                                        control_card_member = m.group(1)
                                        control_card_content = extract_control_card(cntllib_path, control_card_member)
                                    # Save the raw SYSIN DSN statement
                                    sysin_statement = step_line.strip()
                                    break

                            last_step_end = j  # Update last step end index
                            with lock:
                                extracted_data.append((
                                    os.path.basename(file_path), file_type, step_name, "\n".join(step_block),
                                    program_name, sysin_type, sysin_statement, control_card_member, control_card_content,
                                    "\n".join(comment_block)  # Add comments as a separate field
                                ))
        except Exception as e:
            log_error(f"Error reading {file_path}: {str(e)}")

def extract_control_card(cntllib_path, member):
    """ Extract control card content from CNTLLIB """
    if not cntllib_path or not member:
        return "[No CNTLLIB path or member specified]"
        
    try:
        file_path = os.path.join(cntllib_path, member + ".incl")
        if not os.path.exists(file_path):
            # Return a message indicating the file was not found
            return f"[Control card '{member}' not found in CNTLLIB]"
            
        with open(file_path, 'r') as f:
            content = f.read()
            return content if content.strip() else "[Control card file exists but is empty]"
    except Exception as e:
        log_error(f"Error reading control card {member}: {str(e)}")
        return f"[Error reading control card: {str(e)}]"

def log_error(message):
    """ Log error message with timestamp """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Create a log file in the output directory
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".." , "output")
        os.makedirs(output_dir, exist_ok=True)
        log_path = os.path.join(output_dir, "utilitysearch.log")
        
        with open(log_path, "a") as log_file:
            log_file.write(f"{timestamp} - {message}\n")
    except Exception:
        # If we can't write to the log file, just silently continue
        # We don't want to clutter the console with error messages
        pass

def process_files(config):
    """ Main function to process files """
    try:
        # Validate directories
        jcl_dir = config['directories'].get('JCL', '')
        if not os.path.isdir(jcl_dir):
            print(f"JCL directory not found: {jcl_dir}")
            return

        cntllib_path = config['directories'].get('CNTLLIB', '')
        if not os.path.isdir(cntllib_path):
            print(f"CNTLLIB directory not found: {cntllib_path}")
            return
            
        # Validate PROC directory if specified
        proc_dir = config['directories'].get('PROC', '')
        if proc_dir and not os.path.isdir(proc_dir):
            print(f"PROC directory not found: {proc_dir}")
            return
            
        # Set up proc_libraries list
        proc_libraries = []
        if 'proc_libraries' in config:
            proc_libraries = config['proc_libraries']
        elif 'directories' in config and 'PROC' in config['directories']:
            proc_libraries = [config['directories']['PROC']]

        # Load utilities from config
        default_utils = set([u.upper() for u in config.get('default_utilities', [])])
        custom_utils = set([u.upper() for u in config.get('custom_utilities', [])])

        # Create output directory if it doesn't exist
        output_dir = config['output'].get('directory', 'output')
        os.makedirs(output_dir, exist_ok=True)

        # Clear previous data
        global extracted_data
        extracted_data = []

        # Initialize the file queue
        global file_queue
        file_queue = Queue()

        # Add JCL files to the queue
        for root, _, files in os.walk(jcl_dir):
            for file in files:
                if file.endswith('.jcl'):
                    file_path = os.path.join(root, file)
                    file_queue.put((file_path, default_utils.union(custom_utils), "JCL", cntllib_path, proc_libraries))

        # Process files using multiple threads
        threads = []
        num_threads = config.get('performance', {}).get('threads', 4)
        for _ in range(min(num_threads, file_queue.qsize())):
            thread = threading.Thread(target=extract_steps_from_file)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Generate Excel report
        output_filename = config['output'].get('filename', 'jcl_utilities_report')
        if config['output'].get('versioning', True):
            default_file = generate_versioned_filename(os.path.join(output_dir, f"{output_filename}_default.xlsx"))
            custom_file = generate_versioned_filename(os.path.join(output_dir, f"{output_filename}_custom.xlsx"))
        else:
            default_file = os.path.join(output_dir, f"{output_filename}_default.xlsx")
            custom_file = os.path.join(output_dir, f"{output_filename}_custom.xlsx")

        # Create Excel writers
        writer_default = pd.ExcelWriter(default_file, engine='xlsxwriter')
        writer_custom = pd.ExcelWriter(custom_file, engine='xlsxwriter')

        # Create dashboards
        default_dash = [
            [u, 'Yes' if any(r[4]==u for r in extracted_data) else 'No', 
             sum(1 for r in extracted_data if r[4]==u)]
            for u in sorted(default_utils)
        ]
        df_default_dash = pd.DataFrame(default_dash, columns=['Utility','Found','Count'])
        df_default_dash.to_excel(writer_default, sheet_name='Dashboard', index=False)
        
        # Format the workbook
        wb = writer_default.book
        hdr_format = wb.add_format({'bold': True, 'bg_color': '#D7E4BC', 'text_wrap': True, 'valign': 'top'})
        wrap_format = wb.add_format({'text_wrap': True, 'valign': 'top'})
        
        ws_dash = writer_default.sheets['Dashboard']
        for c, v in enumerate(df_default_dash.columns): ws_dash.write(0, c, v, hdr_format)
        for idx, col_val in enumerate(df_default_dash.columns):
            max_len = df_default_dash[col_val].astype(str).map(len).max()
            if pd.isna(max_len): max_len = 0
            max_len = max(max_len, len(str(col_val)))
            ws_dash.set_column(idx, idx, min(int(max_len) + 2, 50), wrap_format)

        # Create utility sheets for default utilities
        for utility in sorted(default_utils):
            data = [r for r in extracted_data if r[4] == utility]
            rows = [(r[0], r[1], r[2], r[9], r[3], r[5], r[6], r[7], r[8]) for r in data]
            df = pd.DataFrame(rows, columns=[
                'File Name', 'File Type', 'Step Name', 'Comments', 'Step',
                'SYSIN Type', 'SYSIN Statement', 'Control Card Member', 'Control Card Content'
            ])
            df.to_excel(writer_default, sheet_name=utility, index=False)
            ws_util = writer_default.sheets[utility]
            for c, v in enumerate(df.columns): ws_util.write(0, c, v, hdr_format)
            for idx, col_val in enumerate(df.columns):
                max_len = df[col_val].astype(str).map(len).max()
                if pd.isna(max_len): max_len = 0
                max_len = max(max_len, len(str(col_val)))
                # Use wrap_format for all columns to ensure text wrapping
                ws_util.set_column(idx, idx, min(int(max_len) + 2, 50), wrap_format)
            
            # Set appropriate row height for all rows to display content without truncation
            for row_idx in range(1, len(df) + 1):
                # Calculate appropriate row height based on content
                max_text_lines = 1
                for col_idx, col_name in enumerate(df.columns):
                    if pd.notna(df.iloc[row_idx-1, col_idx]):
                        text = str(df.iloc[row_idx-1, col_idx])
                        lines = len(text.split('\n'))
                        max_text_lines = max(max_text_lines, lines)
                
                # Set row height (15 points per line of text, with a minimum of 15)
                row_height = max(15, max_text_lines * 15)
                ws_util.set_row(row_idx, row_height)

        writer_default.close()

        # Create custom utilities report
        custom_dash = [
            [u, 'Yes' if any(r[4]==u for r in extracted_data) else 'No', 
             sum(1 for r in extracted_data if r[4]==u)]
            for u in sorted(custom_utils)
        ]
        df_custom_dash = pd.DataFrame(custom_dash, columns=['Utility','Found','Count'])
        df_custom_dash.to_excel(writer_custom, sheet_name='Dashboard', index=False)
        wb_c, h_c, w_c = fmt_book(writer_custom)
        ws_c_dash = writer_custom.sheets['Dashboard']
        for c, v in enumerate(df_custom_dash.columns): ws_c_dash.write(0, c, v, h_c)
        for idx, col_val in enumerate(df_custom_dash.columns):
            max_len = df_custom_dash[col_val].astype(str).map(len).max()
            if pd.isna(max_len): max_len = 0
            max_len = max(max_len, len(str(col_val)))
            ws_c_dash.set_column(idx, idx, min(int(max_len) + 2, 50), w_c)

        for u_custom in sorted(custom_utils):
            data_custom = [r for r in extracted_data if r[4] == u_custom]
            rows_custom = [(r[0], r[1], r[2], r[9], r[3], r[5], r[6], r[7], r[8]) for r in data_custom]
            df_c = pd.DataFrame(rows_custom, columns=[
                'File Name', 'File Type', 'Step Name', 'Comments', 'Step',
                'SYSIN Type', 'SYSIN Statement', 'Control Card Member', 'Control Card Content'
            ])
            df_c.to_excel(writer_custom, sheet_name=u_custom, index=False)
            ws_c_util = writer_custom.sheets[u_custom]
            for c, v in enumerate(df_c.columns): ws_c_util.write(0, c, v, h_c)
            for idx, col_val in enumerate(df_c.columns):
                max_len = df_c[col_val].astype(str).map(len).max()
                if pd.isna(max_len): max_len = 0
                max_len = max(max_len, len(str(col_val)))
                # Use wrap_format for all columns to ensure text wrapping
                ws_c_util.set_column(idx, idx, min(int(max_len) + 2, 50), w_c)
            
            # Set appropriate row height for all rows to display content without truncation
            for row_idx in range(1, len(df_c) + 1):
                # Calculate appropriate row height based on content
                max_text_lines = 1
                for col_idx, col_name in enumerate(df_c.columns):
                    if pd.notna(df_c.iloc[row_idx-1, col_idx]):
                        text = str(df_c.iloc[row_idx-1, col_idx])
                        lines = len(text.split('\n'))
                        max_text_lines = max(max_text_lines, lines)
                
                # Set row height (15 points per line of text, with a minimum of 15)
                row_height = max(15, max_text_lines * 15)
                ws_c_util.set_row(row_idx, row_height)

        writer_custom.close()

        print("\nProcessing complete!\n")
        print(f"Default report: {os.path.basename(default_file)}")
        print(f"Custom report: {os.path.basename(custom_file)}\n")

        found_default_utilities = set(r[4] for r in extracted_data if r[4] in default_utils)
        missing_default = default_utils - found_default_utilities
        if missing_default:
            print(f"Warning: Default utilities not found: {', '.join(sorted(list(missing_default)))}\n")

        found_custom_utilities = set(r[4] for r in extracted_data if r[4] in custom_utils)
        missing_custom = custom_utils - found_custom_utilities
        if missing_custom:
            print(f"Warning: Custom utilities not found: {', '.join(sorted(list(missing_custom)))}\n")
            
        # Single output message for report location
        print(f"JCL Utilities Report saved to {os.path.dirname(default_file)}\n")

    except Exception as e_final:
        # Print a clean, user-friendly error message
        print(f"\nError: An issue occurred during report generation.")
        log_error(f"An error occurred during Excel writing or final summary: {e_final}")
        # Removed the return here to allow execution to continue to if __name__ == '__main__', if applicable when run standalone


def fmt_book(writer):
    wb = writer.book
    hdr = wb.add_format({'bold': True, 'bg_color': '#D7E4BC', 'text_wrap': True, 'valign': 'top'})
    wrap = wb.add_format({'text_wrap': True, 'valign': 'top'})
    return wb, hdr, wrap
