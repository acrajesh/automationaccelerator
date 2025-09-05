import os
import re
import sys
import pandas as pd

def parse_log_file(logfile_path):
    jcl_files = set()
    proc_files = set()
    cntl_files = set()
    jcl_errors = set()
    proc_errors = set()
    cntl_errors = set()
    full_log = []
    
    # Try different encodings in order of preference
    encodings_to_try = ['utf-8', 'latin-1', 'windows-1252', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            with open(logfile_path, 'r', encoding=encoding) as log_file:
                for line in log_file:
                    full_log.append(line.strip())
                    
                    # Handle mvs-jcl format (without subdirectories)
                    jcl_match = re.search(r"(?:.*[\\/])?mvs-jcl[\\/]([\w$@#]+\.jcl)", line, re.IGNORECASE)
                    if jcl_match:
                        jcl_files.add((jcl_match.group(1), "JCL"))
                    
                    # Also try the original mvs-jcls format with subdirectories
                    # Extract JCL files - handle both path formats
                    jcl_match = re.search(r"(?:.*[\\/])?mvs-jcls[\\/](?:jcls)[\\/]([\w$@#]+\.jcl)", line, re.IGNORECASE)
                    if jcl_match:
                        jcl_files.add((jcl_match.group(1), "JCL"))

                    # Extract PROC files - handle both path formats
                    proc_match = re.search(r"(?:.*[\\/])?mvs-jcls[\\/](?:proclib|procs)[\\/]([\w$@#]+)\.jcl", line, re.IGNORECASE)
                    if proc_match:
                        proc_files.add((proc_match.group(1) + ".proc", "PROC"))

                    # Extract CNTL files - handle both path formats
                    cntl_match = re.search(r"(?:.*[\\/])?mvs-jcls[\\/](?:cntllib)[\\/]([\w$@#]+)\.jcl", line, re.IGNORECASE)
                    if cntl_match:
                        cntl_files.add((cntl_match.group(1) + ".ctl", "CNTLCARD"))
                    
                    # Extract JCL errors
                    if ("error:" in line.lower() or "[error]" in line.lower()) and "mvs-jcl" in line:
                        error_match = re.search(r"(?:.*[\\/])?mvs-jcl[\\/]([\w$@#]+\.jcl)", line, re.IGNORECASE)
                        if error_match:
                            jcl_errors.add(error_match.group(1))
                    
                    # Also check for JCL errors in the mvs-jcls format
                    if ("error:" in line.lower() or "[error]" in line.lower()) and "mvs-jcls" in line:
                        error_match = re.search(r"(?:.*[\\/])?mvs-jcls[\\/](?:jcls)[\\/]([\w$@#]+\.jcl)", line, re.IGNORECASE)
                        if error_match:
                            jcl_errors.add(error_match.group(1))

                    # Extract PROC errors - handle both path formats and error indicators
                    if ("error:" in line.lower() or "[error]" in line.lower()) and "mvs-jcls" in line:
                        error_match = re.search(r"(?:.*[\\/])?mvs-jcls[\\/](?:proclib|procs)[\\/]([\w$@#]+)\.jcl", line, re.IGNORECASE)
                        if error_match:
                            proc_errors.add(error_match.group(1) + ".proc")

                    # Extract CNTL errors - handle both path formats and error indicators
                    if ("error:" in line.lower() or "[error]" in line.lower()) and "mvs-jcls" in line:
                        error_match = re.search(r"(?:.*[\\/])?mvs-jcls[\\/](?:cntllib)[\\/]([\w$@#]+)\.jcl", line, re.IGNORECASE)
                        if error_match:
                            cntl_errors.add(error_match.group(1) + ".ctl")
            # If we successfully read the file, break out of the encoding loop
            break
        except UnicodeDecodeError:
            # If this encoding failed, try the next one
            if encoding == encodings_to_try[-1]:
                # If this was the last encoding to try, re-raise the exception
                raise
            continue
            
    return jcl_files, proc_files, cntl_files, jcl_errors, proc_errors, cntl_errors, full_log

def create_inventory_table(file_set, error_set):
    data = []
    for file_name, file_type in file_set:
        status = "Error" if file_name in error_set else "Done"
        data.append([file_name, file_type, status])
    return pd.DataFrame(data, columns=["File Name", "File Type", "Status"])

def create_summary_report(jcl_inv, proc_inv, cntl_inv):
    summary_data = []
    all_total = all_done = all_error = 0
    for name, df in zip(["JCL", "PROC", "CNTLCARD"], [jcl_inv, proc_inv, cntl_inv]):
        total = len(df)
        done = len(df[df["Status"] == "Done"])
        error = len(df[df["Status"] == "Error"])
        done_pct = round((done / total) * 100, 0) if total > 0 else 0
        error_pct = round((error / total) * 100, 0) if total > 0 else 0
        summary_data.append([name, total, done, f"{done_pct}%", error, f"{error_pct}%"])
        all_total += total
        all_done += done
        all_error += error
    
    all_done_pct = round((all_done / all_total) * 100, 0) if all_total > 0 else 0
    all_error_pct = round((all_error / all_total) * 100, 0) if all_total > 0 else 0
    summary_data.append(["ALL", all_total, all_done, f"{all_done_pct}%", all_error, f"{all_error_pct}%"])
    
    return pd.DataFrame(summary_data, columns=["Type", "Total", "Done", "Done Percentage", "Error", "Error Percentage"])

def save_to_excel(jcl_inv, proc_inv, cntl_inv, summary_df, full_log, app_name, output_dir=None):
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{app_name}-jclcodeturn.xlsx")
    else:
        filename = f"{app_name}-jclcodeturn.xlsx"
    
    with pd.ExcelWriter(filename) as writer:
        jcl_inv.to_excel(writer, sheet_name="JCL Inventory", index=False)
        proc_inv.to_excel(writer, sheet_name="PROC Inventory", index=False)
        cntl_inv.to_excel(writer, sheet_name="CNTL Inventory", index=False)
        summary_df.to_excel(writer, sheet_name="JCL Report", index=False)
        pd.DataFrame(full_log, columns=["Log Content"]).to_excel(writer, sheet_name="log-file", index=False)
    print(f"Workbook {filename} created successfully!")

def main():
    output_dir = None
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python jcl_convertlog_scanner.py logfile.log [--output-dir OUTPUT_DIR]")
        return
    
    logfile_path = sys.argv[1]
    
    # Check for output directory argument
    if len(sys.argv) > 2 and sys.argv[2] == "--output-dir" and len(sys.argv) > 3:
        output_dir = sys.argv[3]
    
    app_name = input("Enter application name: ")
    
    jcl_files, proc_files, cntl_files, jcl_errors, proc_errors, cntl_errors, full_log = parse_log_file(logfile_path)
    
    jcl_inv = create_inventory_table(jcl_files, jcl_errors)
    proc_inv = create_inventory_table(proc_files, proc_errors)
    cntl_inv = create_inventory_table(cntl_files, cntl_errors)
    
    summary_df = create_summary_report(jcl_inv, proc_inv, cntl_inv)
    
    save_to_excel(jcl_inv, proc_inv, cntl_inv, summary_df, full_log, app_name, output_dir)

if __name__ == "__main__":
    main()
