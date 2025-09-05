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

file_queue = Queue()
extracted_data = []
lock = threading.Lock()

def extract_calls_from_file():
    while not file_queue.empty():
        file_path, utilities, prefixes = file_queue.get()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            module_name = ""
            for idx, line in enumerate(lines):
                # Try to find module name from START, ENTRY, or NAME
                if not module_name:
                    start_match = re.match(r'\s*(START|ENTRY|NAME)\s+([A-Z0-9_@$#-]+)', line, re.IGNORECASE)
                    if start_match:
                        module_name = start_match.group(2).upper()

            for idx, line in enumerate(lines):
                # Macro or call invocation: usually starts at col 0, but allow for spaces
                # ASM macros often look like: MACRONAME ... or CALL MACRONAME ...
                tokens = re.split(r'\s+', line.strip(), maxsplit=1)
                if not tokens or not tokens[0]:
                    continue
                macro = tokens[0].upper()
                matched_util = None
                # Exact match
                if macro in utilities:
                    matched_util = macro
                else:
                    # Prefix match
                    for prefix in prefixes:
                        if macro.startswith(prefix):
                            matched_util = next((u for u in utilities if u.startswith(prefix)), prefix)
                            break
                if matched_util:
                    # Optionally, grab a few lines of context above
                    context_lines = []
                    for c in range(max(0, idx-2), idx):
                        if lines[c].strip().startswith('*') or lines[c].strip().startswith('**') or lines[c].strip().startswith('//'):
                            context_lines.append(lines[c].strip())
                    snippet = line.strip()
                    with lock:
                        extracted_data.append((os.path.basename(file_path), module_name, idx+1, matched_util, macro, snippet, '\n'.join(context_lines)))
        except Exception as e:
            log_error(f"Error reading {file_path}: {str(e)}")

def log_error(message):
    with open("assembler_utilscan.log", "a") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")

def process_files(config):
    asm_dir = config['directories']['ASSEMBLER']
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

    for file in os.listdir(asm_dir):
        if file.lower().endswith(('.asm', '.s', '.asmb')):
            file_queue.put((os.path.join(asm_dir, file), utilities, prefixes))

    num_threads = min(config['performance'].get('max_threads', 10), file_queue.qsize())
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=extract_calls_from_file)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    results = {}
    for rec in extracted_data:
        util = rec[3]
        if util not in results:
            results[util] = []
        results[util].append(rec)

    with pd.ExcelWriter(output_name, engine='xlsxwriter') as writer:
        dash = []
        for util in sorted(utilities):
            found = 'Yes' if util in results else 'No'
            count = len(results[util]) if util in results else 0
            files = ', '.join(sorted(set(r[0] for r in results.get(util, []))))
            dash.append((util, found, count, files))
        dash_df = pd.DataFrame(dash, columns=['Utility Name','Found','Count','Modules/Files Found In'])
        dash_df.to_excel(writer, sheet_name='Dashboard', index=False)
        fmt_excel(writer, dash_df, 'Dashboard')

        for util, rows in results.items():
            df = pd.DataFrame(rows, columns=['File Name','Module Name','Line Number','Utility Group','Macro/Call Target','Invocation Snippet','Context/Comments'])
            df.drop('Utility Group', axis=1, inplace=True)
            sheet_name = util[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            fmt_excel(writer, df, sheet_name)

    print(f"Processing complete! Output saved to {output_name}")

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
    for col_num, value in enumerate(df.columns.values):
        ws.write(0, col_num, value, header_fmt)
    for idx, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col))
        ws.set_column(idx, idx, min(max_len+2, 50), wrap_fmt)

if __name__ == "__main__":
    config = load_config("config_asm_utilscan.yaml")
    process_files(config)

