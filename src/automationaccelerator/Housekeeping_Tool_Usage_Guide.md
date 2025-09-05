# Housekeeping Tool Distribution - Usage Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Tool Overview](#tool-overview)
4. [Third Party Utilities Report](#third-party-utilities-report)
   - [JCL Utilities Report](#jcl-utilities-report)
   - [COBOL Utilities Report](#cobol-utilities-report)
   - [Assembler Utilities Report](#assembler-utilities-report)
5. [Factory Tool Version Report](#factory-tool-version-report)
6. [Conversion Log Report](#conversion-log-report)
   - [JCL Conversion Log Report](#jcl-conversion-log-report)
   - [COBOL Conversion Log Report](#cobol-conversion-log-report)
   - [Assembler Conversion Log Report](#assembler-conversion-log-report)
7. [IMS Analyzer](#ims-analyzer)
8. [Configuration Files](#configuration-files)
9. [Output Files](#output-files)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)

## Introduction

The Housekeeping Tool Distribution is a comprehensive suite of utilities designed to analyze and report on various aspects of mainframe migration projects. It helps identify third-party utilities used in JCL, COBOL, and Assembler code, analyzes conversion logs, and provides detailed reports on IMS dependencies.

This tool is essential for:
- Identifying third-party utilities that need replacement in a migration project
- Analyzing conversion logs to identify issues and patterns
- Tracking factory tool versions
- Analyzing IMS dependencies in COBOL and Assembler code

## Installation

### Prerequisites
- Windows operating system
- Python 3.6 or higher (if running from source)
- Required Python packages: pandas, xlsxwriter, PyYAML

### Running the Tool
You can run the Housekeeping Tool in two ways:

1. **Using the Executable**:
   - Simply double-click on `housekeeping_cli.exe`
   - All necessary dependencies are bundled with the executable

2. **Running from Source**:
   - Ensure Python 3.6+ is installed
   - Install required packages: `pip install pandas xlsxwriter PyYAML`
   - Run the tool: `python housekeeping_cli.py`

## Tool Overview

The Housekeeping Tool Distribution provides the following main functionalities:

1. **Third Party Utilities Report**:
   - JCL Utilities Report
   - COBOL Utilities Report
   - Assembler Utilities Report

2. **Factory Tool Version Report**:
   - Tracks versions of factory tools used in the project

3. **Conversion Log Report**:
   - JCL Conversion Log Analysis
   - COBOL Conversion Log Analysis
   - Assembler Conversion Log Analysis

4. **IMS Analyzer**:
   - Analyzes IMS dependencies in COBOL and Assembler code

## Third Party Utilities Report

### JCL Utilities Report

The JCL Utilities Report identifies third-party utilities used in JCL files and provides detailed information about each utility's usage.

#### Configuration

Before running the JCL Utilities Report, ensure the configuration file (`config_jcl_utilscan.yaml`) is correctly set up:

```yaml
directories:
  JCL: 'path/to/jcl/files'     # Path to JCL files
  PROC: 'path/to/proc/files'   # Path to PROC files
  CNTLLIB: 'path/to/cntllib'   # Path to CNTLLIB files

default_utilities:
  - ADRDSSU
  - DFSORT
  - SORT
  # Other default utilities...

utilities_file: 'path/to/jcl_utilities.txt'  # Path to custom utilities list

output:
  name: "application_name"  # Application name for naming the output Excel file
  directory: "path/to/output"  # Output directory (optional)
```

#### Running the JCL Utilities Report

1. Start the Housekeeping Tool
2. Select option `1` for "Third Party Utilities Report"
3. Select option `1` for "JCL Utilities Report"
4. Confirm that the configuration file is correct
5. The tool will process all JCL files and generate Excel reports

#### Output

The JCL Utilities Report generates two Excel files:
- `[application_name]-default.xlsx`: Contains information about default utilities
- `[application_name]-custom.xlsx`: Contains information about custom utilities

Each Excel file contains:
- A dashboard sheet with summary information
- Individual sheets for each utility with detailed information:
  - File Name
  - File Type
  - Step Name
  - Comments (preceding the utility step)
  - Step details
  - SYSIN Type
  - SYSIN Statement
  - Control Card Member
  - Control Card Content

### COBOL Utilities Report

The COBOL Utilities Report identifies third-party utilities called from COBOL programs.

#### Configuration

Ensure the configuration file (`config_cobol_utilscan.yaml`) is correctly set up:

```yaml
directories:
  COBOL: 'path/to/cobol/files'  # Path to COBOL files

utilities_file: 'path/to/cobol_utilities.txt'  # Path to custom utilities list

output:
  name: "application_name"  # Application name for naming the output Excel file
```

#### Running the COBOL Utilities Report

1. Start the Housekeeping Tool
2. Select option `1` for "Third Party Utilities Report"
3. Select option `2` for "COBOL Utilities Report"
4. The tool will process all COBOL files and generate Excel reports

### Assembler Utilities Report

The Assembler Utilities Report identifies third-party utilities called from Assembler programs.

#### Configuration

Ensure the configuration file (`config_asm_utilscan.yaml`) is correctly set up:

```yaml
directories:
  ASM: 'path/to/assembler/files'  # Path to Assembler files

utilities_file: 'path/to/zos_assembler_utilities.txt'  # Path to custom utilities list

output:
  name: "application_name"  # Application name for naming the output Excel file
```

#### Running the Assembler Utilities Report

1. Start the Housekeeping Tool
2. Select option `1` for "Third Party Utilities Report"
3. Select option `3` for "Assembler Utilities Report"
4. The tool will process all Assembler files and generate Excel reports

## Factory Tool Version Report

The Factory Tool Version Report tracks versions of factory tools used in the project.

#### Running the Factory Tool Version Report

1. Start the Housekeeping Tool
2. Select option `2` for "Factory Tool Version Report"
3. Enter the path to the factory tools directory
4. The tool will generate a report of all tool versions

## Conversion Log Report

### JCL Conversion Log Report

The JCL Conversion Log Report analyzes JCL conversion logs to identify issues and patterns.

#### Running the JCL Conversion Log Report

1. Start the Housekeeping Tool
2. Select option `3` for "Conversion Log Report"
3. Select option `1` for "JCL Conversion Log Analysis"
4. Enter the path to the JCL conversion log file
5. The tool will analyze the log and generate an Excel report

### COBOL Conversion Log Report

The COBOL Conversion Log Report analyzes COBOL conversion logs to identify issues and patterns.

#### Running the COBOL Conversion Log Report

1. Start the Housekeeping Tool
2. Select option `3` for "Conversion Log Report"
3. Select option `2` for "COBOL Conversion Log Analysis"
4. Enter the path to the COBOL conversion log file
5. The tool will analyze the log and generate an Excel report

### Assembler Conversion Log Report

The Assembler Conversion Log Report analyzes Assembler conversion logs to identify issues and patterns.

#### Running the Assembler Conversion Log Report

1. Start the Housekeeping Tool
2. Select option `3` for "Conversion Log Report"
3. Select option `3` for "Assembler Conversion Log Analysis"
4. Enter the path to the Assembler conversion log file
5. The tool will analyze the log and generate an Excel report

## IMS Analyzer

The IMS Analyzer identifies IMS dependencies in COBOL and Assembler code.

#### Running the IMS Analyzer

1. Start the Housekeeping Tool
2. Select option `4` for "IMS Analyzer"
3. Enter the path to the COBOL programs folder
4. Enter the path to the COBOL Copybooks folder
5. Enter the path to the ASM (Assembler listing) folder
6. The tool will analyze the code and generate an Excel report

## Configuration Files

The Housekeeping Tool uses several configuration files:

### JCL Utilities Configuration (`config_jcl_utilscan.yaml`)

```yaml
directories:
  JCL: 'path/to/jcl/files'
  PROC: 'path/to/proc/files'
  CNTLLIB: 'path/to/cntllib'

default_utilities:
  - ADRDSSU
  - DFSORT
  # Other default utilities...

utilities_file: 'path/to/jcl_utilities.txt'

output:
  name: "application_name"
  versioning: true

logging:
  log_file: 'utilityscan.log'

excel_format:
  bold_headers: true
  auto_size_columns: true
  wrap_text: true

performance:
  parallel_processing: true
  max_threads: 10

error_handling:
  report_missing_utilities: true
  log_scan_anomalies: true
  handle_corrupted_files: true
```

### COBOL Utilities Configuration (`config_cobol_utilscan.yaml`)

```yaml
directories:
  COBOL: 'path/to/cobol/files'

utilities_file: 'path/to/cobol_utilities.txt'

output:
  name: "application_name"
```

### Assembler Utilities Configuration (`config_asm_utilscan.yaml`)

```yaml
directories:
  ASM: 'path/to/assembler/files'

utilities_file: 'path/to/zos_assembler_utilities.txt'

output:
  name: "application_name"
```

### Utility List Files

- `jcl_utilities.txt`: List of custom JCL utilities to scan for
- `cobol_utilities.txt`: List of custom COBOL utilities to scan for
- `zos_assembler_utilities.txt`: List of custom Assembler utilities to scan for

## Output Files

All output files are stored in the `output` directory, organized by tool:

- `output/jcl_utilities/`: JCL Utilities Reports
- `output/cobol_utilities/`: COBOL Utilities Reports
- `output/asm_utilities/`: Assembler Utilities Reports
- `output/jcl_conversion_logs/`: JCL Conversion Log Reports
- `output/cobol_conversion_logs/`: COBOL Conversion Log Reports
- `output/asm_conversion_logs/`: Assembler Conversion Log Reports
- `output/ims_analysis/`: IMS Analysis Reports
- `output/tool_versions/`: Factory Tool Version Reports

## Troubleshooting

### Common Issues

1. **Configuration File Not Found**:
   - Ensure the configuration files are in the `config` directory
   - If running as an executable, the config files should be in the same directory as the executable or in a `config` subdirectory

2. **Invalid Directory Paths**:
   - Ensure all directory paths in the configuration files are valid
   - Use absolute paths to avoid any issues with relative paths

3. **Missing Utility List Files**:
   - Ensure the utility list files are in the correct location as specified in the configuration files

4. **Excel File Already Open**:
   - Close any open Excel files before running the tool to avoid file access issues

5. **Performance Issues**:
   - Adjust the `max_threads` parameter in the configuration files to optimize performance
   - For large codebases, increase the number of threads for better performance

## Advanced Usage

### Custom Utility Lists

You can create custom utility lists by editing the utility list files:

- `jcl_utilities.txt`: Add one utility name per line
- `cobol_utilities.txt`: Add one utility name per line
- `zos_assembler_utilities.txt`: Add one utility name per line

### Running from Command Line

You can run specific tools directly from the command line:

```bash
# Run JCL Utilities Scanner
python -m housekeeping_modules.jcl_utilscan --config path/to/config_jcl_utilscan.yaml

# Run COBOL Utilities Scanner
python -m housekeeping_modules.cobol_utilscan --config path/to/config_cobol_utilscan.yaml

# Run Assembler Utilities Scanner
python -m housekeeping_modules.asm_utilscan --config path/to/config_asm_utilscan.yaml
```

### Customizing Excel Output

The Excel output can be customized by modifying the configuration files:

```yaml
excel_format:
  bold_headers: true  # Ensures headers are bold
  auto_size_columns: true  # Automatically resizes columns for better readability
  wrap_text: true  # Enables text wrapping in cells
```

Recent improvements include:
- Dynamic row height adjustment based on content
- Text wrapping for all cells
- Vertical alignment for better readability

This ensures that all content, especially multi-line comments, is fully visible without requiring double-clicking to expand cells.

---

This usage guide provides a comprehensive overview of the Housekeeping Tool Distribution. For additional assistance or to report issues, please contact the tool maintainer.
