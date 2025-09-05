import sys
import re
import os
import pandas as pd
from openpyxl import Workbook

def parse_log_file(log_file):
    conversion_summary = []
    
    # Try different encodings in order of preference
    encodings_to_try = ['utf-8', 'latin-1', 'windows-1252', 'cp1252']
    lines = None
    
    for encoding in encodings_to_try:
        try:
            with open(log_file, 'r', encoding=encoding) as file:
                lines = file.readlines()
            print(f"Successfully read file using {encoding} encoding")
            break  # If successful, break out of the loop
        except UnicodeDecodeError:
            print(f"Failed to read with {encoding} encoding, trying next...")
            if encoding == encodings_to_try[-1]:  # If this is the last encoding to try
                raise  # Re-raise the exception if all encodings fail
            continue  # Otherwise try the next encoding
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if "Parsing file" in line:
            # Updated pattern to handle different path formats
            program_name_match = re.search(r'(?:.*[\\/])?assembler-listings[\\/](.*?)\.txt', line)
            if program_name_match:
                program_name = program_name_match.group(1)
                j = i + 1
                error_flag = False
                converting_found = False
                
                # Checking for errors between Parsing and Converting
                while j < len(lines) and "Converting file" not in lines[j]:
                    if "[error]" in lines[j]:
                        error_flag = True
                    j += 1
                
                # Move past the Converting file line
                if j < len(lines) and "Converting file" in lines[j]:
                    converting_found = True
                    j += 1
                
                # Checking for errors after Converting but before next Parsing or Unique error messages
                while j < len(lines):
                    if "Parsing file" in lines[j] or "Unique error messages:" in lines[j]:
                        break
                    if "[error]" in lines[j]:
                        error_flag = True
                    j += 1
                
                conversion_summary.append([program_name, "Error" if error_flag else "Done"])
                i = j - 1  # Ensuring correct loop progression
        i += 1
    
    return conversion_summary

def generate_asm_report(conversion_summary):
    total = len(conversion_summary)
    done_count = sum(1 for _, status in conversion_summary if status == "Done")
    error_count = total - done_count
    done_percentage = round((done_count / total) * 100) if total > 0 else 0
    error_percentage = round((error_count / total) * 100) if total > 0 else 0
    
    return [["Assembler programs", total, done_count, f"{done_percentage}%", error_count, f"{error_percentage}%"]]

def save_to_excel(app_name, conversion_summary, asm_report, output_dir=None):
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Conversion Summary"
    
    ws1.append(["Program", "Conversion Summary"])
    for row in conversion_summary:
        ws1.append(row)
    
    ws2 = wb.create_sheet(title="ASM Report")
    ws2.append(["Type", "Total", "Done", "Done Percentage", "Error", "Error Percentage"])
    for row in asm_report:
        ws2.append(row)
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        file_name = os.path.join(output_dir, f"{app_name}.xlsx")
    else:
        file_name = f"{app_name}.xlsx"
        
    wb.save(file_name)
    print(f"Report saved as {file_name}")

def main():
    output_dir = None
    
    if len(sys.argv) < 2:
        print("Usage: python asm_convertlog_scanner.py logfile.log [--output-dir OUTPUT_DIR]")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    # Check for output directory argument
    if len(sys.argv) > 2 and sys.argv[2] == "--output-dir" and len(sys.argv) > 3:
        output_dir = sys.argv[3]
    
    app_name = input("Enter App Name: ")
    
    conversion_summary = parse_log_file(log_file)
    asm_report = generate_asm_report(conversion_summary)
    save_to_excel(app_name, conversion_summary, asm_report, output_dir)

if __name__ == "__main__":
    main()
