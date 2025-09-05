import sys
import os

# Ensure modules are importable
# sys.path manipulation removed for packaging

import importlib


def ensure_output_dir(tool_type):
    """
    Create and ensure the output directory structure exists for the specified tool type.
    Uses ~/.autoaccel/output by default (or AUTOACCEL_OUTPUT_BASE if set), and falls back
    to the executable directory when running as a single-file build.
    """
    import os, sys
    # Preferred base: env or user home
    base_output_dir = os.environ.get("AUTOACCEL_OUTPUT_BASE")
    if not base_output_dir:
        base_output_dir = os.path.join(os.path.expanduser("~"), ".autoaccel", "output")

    # If frozen (PyInstaller), also create a colocated output dir for portability
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        try:
            os.makedirs(os.path.join(exe_dir, "output"), exist_ok=True)
        except Exception:
            # ignore if not permitted; still use home dir
            pass

    os.makedirs(base_output_dir, exist_ok=True)
    tool_output_dir = os.path.join(base_output_dir, tool_type)
    os.makedirs(tool_output_dir, exist_ok=True)
    return tool_output_dir


while True:
    print("\nAutomation Accelerator\n")
    print("1. Third Party Utilities Report")
    print("2. Factory Tool Version Report")
    print("3. Conversion Log Report")
    print("4. IMS Analyzer")
    print("5. Exit")
    choice = input("\nEnter your choice (1-5): ").strip()
    if choice == '1':
        # Third Party Utilities Report - Nested Menu
        while True:
            print("\nThird Party Utilities Report")
            print("1. JCL Utilities Report")
            print("2. COBOL Utilities Report")
            print("3. Assembler Utilities Report")
            print("4. Return to Main Menu")
            sub_choice = input("\nEnter your choice (1-4): ").strip()
            
            if sub_choice == '1':
                # JCL Utilities Scan
                print("ALERT: Please validate that the YAML configuration file (config_jcl_utilscan.yaml) is correct before proceeding.")
                proceed = input("Do you want to continue? (Y to proceed, any other key to exit): ").strip().lower()
                if proceed != 'y':
                    print("Operation cancelled by user.")
                    continue
                try:
                    # Create output directory for JCL utilities
                    output_dir = ensure_output_dir("jcl_utilities")
                    
                    jcl_utilscan = importlib.import_module('modules.jcl_utilscan')
                    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
                    config_name = "config_jcl_utilscan.yaml"
                    config_dir = os.path.join(exe_dir, "config")
                    config_path = os.path.join(config_dir, config_name)
                    if not os.path.exists(config_path):
                        print(f"Required file '{config_name}' not found in {config_dir}. Please place '{config_name}' in the config directory.")
                        continue
                    config = jcl_utilscan.load_config(config_path)
                    
                    # Add output directory to config if the module supports it
                    if hasattr(jcl_utilscan, 'add_output_dir_to_config'):
                        config = jcl_utilscan.add_output_dir_to_config(config, output_dir)
                    
                    jcl_utilscan.process_files(config)
                    print(f"JCL Utilities Report saved to {output_dir}")
                except Exception as e:
                    print(f"Error running JCL utilities scan: {e}")
            
            elif sub_choice == '2':
                # COBOL Utilities Scan
                try:
                    # Create output directory for COBOL utilities
                    output_dir = ensure_output_dir("cobol_utilities")
                    
                    cobol_utilscan = importlib.import_module('modules.cobol_utilscan')
                    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
                    config_name = "config_cobol_utilscan.yaml"
                    config_dir = os.path.join(exe_dir, "config")
                    config_path = os.path.join(config_dir, config_name)
                    if not os.path.exists(config_path):
                        print(f"Required file '{config_name}' not found in {config_dir}. Please place '{config_name}' in the config directory.")
                        continue
                    config = cobol_utilscan.load_config(config_path)
                    
                    # Add output directory to config if the module supports it
                    if hasattr(cobol_utilscan, 'add_output_dir_to_config'):
                        config = cobol_utilscan.add_output_dir_to_config(config, output_dir)
                        
                    cobol_utilscan.process_files(config)
                    print(f"COBOL Utilities Report saved to {output_dir}")
                except Exception as e:
                    print(f"Error running cobol_utilscan: {e}")
            
            elif sub_choice == '3':
                # Assembler Utilities Scan
                try:
                    # Create output directory for ASM utilities
                    output_dir = ensure_output_dir("asm_utilities")
                    
                    asm_utilscan = importlib.import_module('modules.asm_utilscan')
                    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
                    config_name = "config_asm_utilscan.yaml"
                    config_dir = os.path.join(exe_dir, "config")
                    config_path = os.path.join(config_dir, config_name)
                    if not os.path.exists(config_path):
                        print(f"Required file '{config_name}' not found in {config_dir}. Please place '{config_name}' in the config directory.")
                        continue
                    config = asm_utilscan.load_config(config_path)
                    
                    # Add output directory to config if the module supports it
                    if hasattr(asm_utilscan, 'add_output_dir_to_config'):
                        config = asm_utilscan.add_output_dir_to_config(config, output_dir)
                        
                    asm_utilscan.process_files(config)
                    print(f"Assembler Utilities Report saved to {output_dir}")
                except Exception as e:
                    print(f"Error running asm_utilscan: {e}")
            
            elif sub_choice == '4':
                # Return to main menu
                break
            
            else:
                print("Invalid option. Please select 1, 2, 3, or 4.")
    elif choice == '2':
        # Factory Tool Version Report
        try:
            # Create output directory for tool version reports
            output_dir = ensure_output_dir("tool_versions")
            
            # Import the tool version report module
            tool_version_report = importlib.import_module('modules.tool_version_report')
            
            print("\nRunning Factory Tool Version Report...\n")
            tools_dir = input("Please enter the full path to your tools directory (e.g. D:/factory/tools): ").strip()
            app_name = input("Please enter an application name to prefix the report file (e.g. myapp): ").strip()
            
            # Generate the report file path
            report_file = os.path.join(output_dir, f"{app_name}_tools_report.xlsx")
            
            # Run the tool version report
            df = tool_version_report.scan_tools(tools_dir, report_file)
            tool_version_report.display_selected_tools(df)
        except Exception as e:
            print(f'Error running tool version report: {e}')
    elif choice == '3':
        # Conversion Log Report - Nested Menu
        while True:
            print("\nConversion Log Report")
            print("1. JCL Conversion Log Report")
            print("2. COBOL Conversion Log Report")
            print("3. Assembler Conversion Log Report")
            print("4. Return to Main Menu")
            sub_choice = input("\nEnter your choice (1-4): ").strip()
            
            if sub_choice == '1':
                # JCL Conversion Log Analysis
                try:
                    # Get log file path
                    log_file_path = input("Enter the full path to the JCL conversion log file: ").strip()
                    if not os.path.exists(log_file_path):
                        print(f"Error: Log file {log_file_path} not found!")
                        continue
                    
                    # Create output directory for JCL conversion logs
                    output_dir = ensure_output_dir("jcl_conversion_logs")
                    
                    # Import and run the JCL scanner from modules
                    import modules.jcl_convertlog_scanner as jclscanner
                    
                    # Set up sys.argv for the JCL scanner with output directory
                    sys.argv = [sys.argv[0], log_file_path, "--output-dir", output_dir]
                    
                    # Run the JCL scanner
                    jclscanner.main()
                    print(f"JCL Conversion Log Analysis completed. Report saved to {output_dir}")
                    
                    # Reset sys.argv to avoid issues with other modules
                    sys.argv = [sys.argv[0]]
                    
                except Exception as e:
                    print(f"Error running JCL conversion log analysis: {e}")
            
            elif sub_choice == '2':
                # COBOL Conversion Log Analysis
                try:
                    # Get log file path
                    log_file_path = input("Enter the full path to the COBOL conversion log file: ").strip()
                    if not os.path.exists(log_file_path):
                        print(f"Error: Log file {log_file_path} not found!")
                        continue
                    
                    # Create output directory for COBOL conversion logs
                    output_dir = ensure_output_dir("cobol_conversion_logs")
                    
                    # Import and run the COBOL scanner from modules
                    import modules.cobol_convertlog_scanner as cobolscanner
                    
                    # Run the COBOL scanner with output directory
                    cobolscanner.create_excel_report(log_file_path, output_dir)
                    print(f"COBOL Conversion Log Analysis completed. Report saved to {output_dir}")
                    
                except Exception as e:
                    print(f"Error running COBOL conversion log analysis: {e}")
            
            elif sub_choice == '3':
                # Assembler Conversion Log Analysis
                try:
                    # Get log file path
                    log_file_path = input("Enter the full path to the Assembler conversion log file: ").strip()
                    if not os.path.exists(log_file_path):
                        print(f"Error: Log file {log_file_path} not found!")
                        continue
                    
                    # Create output directory for ASM conversion logs
                    output_dir = ensure_output_dir("asm_conversion_logs")
                    
                    # Import and run the Assembler scanner from modules
                    import modules.asm_convertlog_scanner as asmscanner
                    
                    # Set up sys.argv for the ASM scanner with output directory
                    sys.argv = [sys.argv[0], log_file_path, "--output-dir", output_dir]
                    
                    # Run the Assembler scanner
                    asmscanner.main()
                    print(f"Assembler Conversion Log Analysis completed. Report saved to {output_dir}")
                    
                    # Reset sys.argv to avoid issues with other modules
                    sys.argv = [sys.argv[0]]
                    
                except Exception as e:
                    print(f"Error running Assembler conversion log analysis: {e}")
            
            elif sub_choice == '4':
                # Return to main menu
                break
            
            else:
                print("Invalid option. Please select 1, 2, 3, or 4.")
    
    elif choice == '4':
        # IMS Analyzer
        try:
            # Create output directory for IMS analysis
            output_dir = ensure_output_dir("ims_analysis")
            
            ims_analyzer = importlib.import_module('modules.ims_analyzer')
            print('Running IMS Analyzer...')
            
            # Get input from user
            cobol_folder = input("Enter the path to the COBOL programs folder: ").strip()
            copybook_folder = input("Enter the path to the COBOL Copybooks folder: ").strip()
            asm_folder = input("Enter the path to the ASM (Assembler listing) folder: ").strip()
            
            if not cobol_folder or not copybook_folder or not asm_folder:
                print('All folder paths are required.')
                continue
                
            # Run the analyzer with the provided paths
            summary_data, call_inventory, param_counts, function_counts = ims_analyzer.scan_all(cobol_folder, copybook_folder, asm_folder)
            
            # Generate report in the output directory
            report_file = os.path.join(output_dir, "IMS_Impact_Report.xlsx")
            ims_analyzer.generate_final_excel_report_with_clean_params(summary_data, call_inventory, param_counts, function_counts, output_dir=output_dir)
            
            print(f"IMS Analysis Report saved to {output_dir}")
        except Exception as e:
            print(f'Error running IMS Analyzer: {e}')
            
    elif choice == '5':
        print("Exiting.")
        break
    else:
        print("Invalid option. Please select 1, 2, 3, 4, or 5.")
