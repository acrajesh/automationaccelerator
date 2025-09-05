import os
import re
import yaml
import pandas as pd
import threading
from queue import Queue
from datetime import datetime
import xlsxwriter

# === CONFIG LOADING ===
def load_config(yaml_file):
    if not os.path.exists(yaml_file):
        print(f"Configuration file '{yaml_file}' not found! Exiting.")
        exit(1)
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def add_output_dir_to_config(config, output_dir):
    """ Add output directory to configuration """
    if 'output' not in config:
        config['output'] = {}
    config['output']['directory'] = output_dir
    return config

def load_utilities(util_file):
    if not os.path.exists(util_file):
        print(f"Utility list file '{util_file}' not found! Exiting.")
        exit(1)
    with open(util_file, 'r') as f:
        utils = set(line.strip().upper() for line in f if line.strip())
    prefixes = set(u[:3] for u in utils if len(u) >= 3)
    return utils, prefixes

# === GLOBALS ===
file_queue = Queue()
extracted_data = []
lock = threading.Lock()

# === COBOL SCAN WORKER ===
def extract_calls_from_file():
    while not file_queue.empty():
        file_path, utilities, prefixes = file_queue.get()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            program_name = ""
            for idx, line in enumerate(lines):
                # Find PROGRAM-ID if available
                if not program_name:
                    prog_match = re.match(r'\s*PROGRAM-ID\s*\.\s*([A-Z0-9_-]+)', line, re.IGNORECASE)
                    if prog_match:
                        program_name = prog_match.group(1).upper()

            for idx, line in enumerate(lines):
                call_match = re.search(r'CALL\s+[\'\"]?([A-Z0-9_#$@-]+)[\'\"]?', line, re.IGNORECASE)
                if call_match:
                    util_name = call_match.group(1).upper()
                    matched_util = None
                    # Exact match
                    if util_name in utilities:
                        matched_util = util_name
                    else:
                        # Prefix match
                        for prefix in prefixes:
                            if util_name.startswith(prefix):
                                matched_util = next((u for u in utilities if u.startswith(prefix)), prefix)
                                break
                    if matched_util:
                        # Grab context comments from lines above
                        context_lines_above = []
                        for c_idx in range(max(0, idx - 2), idx):
                            line_content = lines[c_idx]
                            # Check for fixed-format comment (asterisk in column 7) or free-format comment
                            if (len(line_content) > 6 and line_content[6] == '*') or \
                               line_content.strip().startswith("*>"):
                                context_lines_above.append(line_content.rstrip('\n'))

                        # Capture the full COBOL statement including explicit continuations
                        statement_lines = []
                        
                        # Add the line where CALL was found
                        current_line_to_add = lines[idx]
                        statement_lines.append(current_line_to_add.rstrip('\n'))
                        
                        # Check subsequent lines for explicit hyphen continuation
                        next_line_cursor = idx + 1
                        # Limit lookahead to avoid excessive processing on malformed files or very long statements
                        max_continuation_lines = 10 # Max number of continuation lines to check
                        for _ in range(max_continuation_lines):
                            if next_line_cursor >= len(lines):
                                break # End of file

                            potential_continuation_line = lines[next_line_cursor]
                            
                            # Check for hyphen in column 7 (indicator area)
                            if len(potential_continuation_line) > 6 and potential_continuation_line[6] == '-':
                                statement_lines.append(potential_continuation_line.rstrip('\n'))
                                next_line_cursor += 1
                            else:
                                # Not an explicit continuation line with hyphen, so statement ends here
                                break
                        
                        snippet = "\n".join(statement_lines)

                        with lock:
                            extracted_data.append((
                                os.path.basename(file_path),
                                program_name,
                                idx + 1,  # Line number of the start of the CALL
                                matched_util,
                                util_name, # The actual target of CALL
                                snippet,  # The potentially multi-line statement
                                '\n'.join(context_lines_above) # Use the new variable for context comments
                            ))
        except Exception as e:
            log_error(f"Error reading {file_path}: {str(e)}")

# === LOGGING ===
def log_error(message):
    with open("cobol_utilscan.log", "a") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

# === MAIN PROCESS ===
def process_files(config):
    # Clear previous run data
    global extracted_data, file_queue
    extracted_data = []
    # Clear the queue by re-initializing it or draining it
    while not file_queue.empty():
        try:
            file_queue.get_nowait() # Drain existing items
        except Queue.Empty:
            break # Should not happen if not empty, but good practice
    # Alternatively, re-initialize: file_queue = Queue()

    cobol_dir = config['directories']['COBOL']
    util_file = config['utilities_file']
    
    # Check if output directory is specified
    output_dir = config['output'].get('directory')
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_name = os.path.join(output_dir, config['output']['name'] + ".xlsx")
    else:
        output_name = config['output']['name'] + ".xlsx"
        
    output_name = generate_versioned_filename(output_name) if config['output'].get('versioning', True) else output_name
    utilities, prefixes = load_utilities(util_file)

    # Queue all COBOL files
    for file in os.listdir(cobol_dir):
        if file.lower().endswith(('.cob', '.cbl', '.cobol')):
            file_queue.put((os.path.join(cobol_dir, file), utilities, prefixes))

    num_threads = min(config['performance'].get('max_threads', 10), file_queue.qsize())
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=extract_calls_from_file)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    # Organize results by utility
    results = {}
    for rec in extracted_data:
        util = rec[3]
        if util not in results:
            results[util] = []
        results[util].append(rec)

    # === EXCEL OUTPUT ===
    with pd.ExcelWriter(output_name, engine='xlsxwriter') as writer:
        # Dashboard sheet
        dash = []
        for util in sorted(utilities):
            found = 'Yes' if util in results else 'No'
            count = len(results[util]) if util in results else 0
            files = ', '.join(sorted(set(r[0] for r in results.get(util, []))))
            dash.append((util, found, count, files))
        dash_df = pd.DataFrame(dash, columns=['Utility Name','Found','Count','Programs/Files Found In'])
        dash_df.to_excel(writer, sheet_name='Dashboard', index=False)
        fmt_excel(writer, dash_df, 'Dashboard')

        # One sheet per utility found
        for util, rows in results.items():
            df = pd.DataFrame(rows, columns=['File Name','Program Name','Line Number','Utility Group','Call Target','Call Snippet','Context/Comments'])
            df.drop('Utility Group', axis=1, inplace=True)
            sheet_name = util[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            fmt_excel(writer, df, sheet_name)

    print(f"Processing complete! Output saved to {output_name}")

# === UTILITY ===
def generate_versioned_filename(base_filename):
    if not os.path.exists(base_filename):
        return base_filename
    version = 1
    file_root, file_ext = os.path.splitext(base_filename)
    while os.path.exists(f"{file_root}_v{version}{file_ext}"):
        version += 1
    return f"{file_root}_v{version}{file_ext}"

def fmt_excel(writer, df, sheet):
    wb = writer.book
    ws = writer.sheets[sheet]
    header_fmt = wb.add_format({'bold': True, 'bg_color': '#D9E1F2'})
    wrap_fmt = wb.add_format({'text_wrap': True})
    # Bold headers
    for col_num, value in enumerate(df.columns.values):
        ws.write(0, col_num, value, header_fmt)
    # Auto-size columns
    for idx, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col))
        ws.set_column(idx, idx, min(max_len+2, 50), wrap_fmt)

# === ENTRY POINT ===
if __name__ == "__main__":
    config = load_config("config_cobol_utilscan.yaml")
    process_files(config)
