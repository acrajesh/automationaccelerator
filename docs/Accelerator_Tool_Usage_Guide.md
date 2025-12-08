# Accelerator Tool Usage Guide

---

## Table of Contents

[1. Introduction](#1-introduction)  
[2. Architecture and Concepts](#2-architecture-and-concepts)  
[3. Installation and Prerequisites](#3-installation-and-prerequisites)  
[4. Output Directory Behavior](#4-output-directory-behavior)  
[5. Using the CLI: Main Menu Walkthrough](#5-using-the-cli-main-menu-walkthrough)  
[6. Accelerator: Third Party Utilities Report](#6-accelerator-third-party-utilities-report)  
[7. Accelerator: Factory Tool Version Report](#7-accelerator-factory-tool-version-report)  
[8. Accelerator: Conversion Log Report](#8-accelerator-conversion-log-report)  
[9. Accelerator: IMS Analyzer](#9-accelerator-ims-analyzer)  
[10. Configuration Files and Customization](#10-configuration-files-and-customization)  
[11. End-to-End Usage Examples](#11-end-to-end-usage-examples)  
[12. Troubleshooting and Common Pitfalls](#12-troubleshooting-and-common-pitfalls)  
[13. Reference: Menu Map and Modules](#13-reference-menu-map-and-modules)  
[Appendix: Quick Reference Card](#appendix-quick-reference-card)  

---

## 1. Introduction

### What Is the Accelerator House?

The **Accelerator  House** is a collection of analysis and reporting utilities designed to support mainframe modernization projects. Previously referred to as "housekeeping tools," these accelerators help teams discover what's really happening in legacy environments and turn scattered code, logs, and configurations into actionable intelligence and architecture-ready documentation.

**In plain terms**: When organizations move applications off mainframes, they face challenges like understanding what external tools their code depends on, tracking conversion progress, and identifying potential risks. The Accelerator Tool House consolidates that scattered information into clear, shareable Excel reports and inventories so that engineers, analysts, and executives can make confident decisions about migration scope, sequencing, and risk.

By generating structured knowledge bases from legacy artifacts, these accelerators support modernization planning, reduce downtime risk, and help delivery pipelines move forward with confidence.

### Why This Matters to Your Project

- **Discover applications and build knowledge bases**: Turn legacy scripts, job streams, and logs into a living, structured knowledge base that supports architecture diagrams, runbooks, and handover documentation
- **Generate actionable intelligence**: Transform complex technical data into clear insights that drive planning decisions, risk assessments, and resource allocation
- **Reduce risk and downtime**: Identify hidden dependencies and problem areas before they cause production incidents or migration delays
- **Simplify modernization programs**: Feed clean, structured data into your modernization pipeline so teams can focus on remediation and redesign, not manual data gathering
- **Support delivery pipelines with confidence**: Enable transparency across technical and business stakeholders with reports that can be understood and discussed at any level

### Accelerators at a Glance

| Accelerator | What It Does | Business Value |
|-------------|--------------|----------------|
| **Third Party Utilities Report** | Scans JCL, COBOL, and Assembler code to find third-party utility usage | Identifies external dependencies that may need licensing, replacement, or special handling during migration |
| **Factory Tool Version Report** | Inventories tools in a directory and reports their versions | Ensures environment consistency and validates tooling before and after migration |
| **Conversion Log Report** | Parses conversion log files into structured Excel reports | Quickly surfaces errors, warnings, and statistics from verbose logs—critical for tracking conversion quality |
| **IMS Analyzer** | Analyzes code to identify IMS database calls and patterns | Assesses IMS complexity and impact, essential for planning IMS-to-modern-database migrations |

> **Jargon Quick Reference**:
> - **JCL (Job Control Language)**: A scripting language used on mainframes to run batch jobs
> - **COBOL**: A programming language commonly used in mainframe business applications
> - **Assembler**: Low-level programming language used for performance-critical mainframe code
> - **IMS (Information Management System)**: IBM's hierarchical database system used by many mainframe applications
> - **Copybook**: Reusable code snippets in COBOL, similar to header files or includes in other languages

### Who Should Use This Guide

This guide serves **all stakeholders** involved in modernization projects:

| If you are a... | Start with... |
|-----------------|---------------|
| **Executive or sponsor** | [Introduction](#1-introduction) and [End-to-End Examples](#11-end-to-end-usage-examples) for business context |
| **Project manager or analyst** | [Introduction](#1-introduction), then skim each accelerator's "For Non-Technical Readers" sections |
| **Architect** | [Architecture and Concepts](#2-architecture-and-concepts) and individual accelerator sections |
| **Engineer or operator** | [Installation](#3-installation-and-prerequisites), then detailed sections for accelerators you'll run |
| **Anyone troubleshooting** | [Troubleshooting](#12-troubleshooting-and-common-pitfalls) and [Quick Reference](#appendix-quick-reference-card) |

### Typical Use Cases

- **Pre-migration assessment**: Identify third-party utilities and IMS dependencies before starting migration work
- **Environment validation**: Confirm tool versions match requirements across development, test, and production
- **Conversion monitoring**: Track errors and warnings from conversion tools to prioritize fixes
- **Stakeholder reporting**: Generate Excel reports for status meetings, steering committees, or vendor discussions

[Back to top](#accelerator-tool-usage-guide)

---

## 2. Architecture and Concepts

> **For non-technical readers**: Think of the Accelerator Tool House as a **toolbox with specialized instruments**—each designed to examine a different aspect of your legacy system. You don't need to understand how each tool works internally; you just need to know which tool to pick for the job and what report it will produce. If the technical details in this section feel overwhelming, skip ahead to [End-to-End Usage Examples](#11-end-to-end-usage-examples) for practical walkthroughs.

### The Accelerator CLI

The **Accelerator CLI** (Command Line Interface) is a menu-driven, interactive program that serves as the single entry point to all accelerators. When launched, it presents a main menu; selecting an option either runs an accelerator directly or opens a nested submenu for more specific choices.

**Simple analogy**: The CLI is like the front desk of a service center. You walk in, choose what service you need from a menu, provide the necessary information, and receive your report.

### Menu Structure

```
Main Menu
├── 1. Third Party Utilities Report
│   ├── 1. JCL Utilities Report
│   ├── 2. COBOL Utilities Report
│   ├── 3. Assembler Utilities Report
│   └── 4. Return to Main Menu
├── 2. Factory Tool Version Report
├── 3. Conversion Log Report
│   ├── 1. JCL Conversion Log Report
│   ├── 2. COBOL Conversion Log Report
│   ├── 3. Assembler Conversion Log Report
│   └── 4. Return to Main Menu
├── 4. IMS Analyzer
└── 5. Exit
```

### Relationship Between CLI and Modules

The CLI does not contain the analysis logic itself. Instead, it:

1. Presents menus and collects user input
2. Dynamically imports the appropriate module from the `modules` package
3. Passes configuration and paths to the module's entry-point functions
4. Directs output to a per-accelerator subdirectory

### Per-Accelerator Output Directories

Each accelerator writes its outputs to a dedicated subdirectory under a common base output folder. This keeps reports organized and prevents file collisions.

| Accelerator | Output Subdirectory |
|-------------|---------------------|
| JCL Utilities Report | `jcl_utilities` |
| COBOL Utilities Report | `cobol_utilities` |
| Assembler Utilities Report | `asm_utilities` |
| Factory Tool Version Report | `tool_versions` |
| JCL Conversion Log Report | `jcl_conversion_logs` |
| COBOL Conversion Log Report | `cobol_conversion_logs` |
| Assembler Conversion Log Report | `asm_conversion_logs` |
| IMS Analyzer | `ims_analysis` |

[Back to top](#accelerator-tool-usage-guide)

---

## 3. Installation and Prerequisites

> **For non-technical readers**: This section covers setup requirements. If someone else is installing and running the tools for you, you can skip this section. If you need reports generated, share this section with your technical team so they can set things up correctly.

### Python Runtime

The Accelerator CLI is written in Python. It requires:

- **Python 3.x** (exact version depends on module dependencies)
- Required packages as specified in your project's dependency file (e.g., `requirements.txt`)

### Distribution Modes

#### Running from Source

When running from source:

- The CLI script resides in the `src/automationaccelerator/` directory
- The `modules` package must be importable (typically via `PYTHONPATH` or installed as a package)
- The `config` directory must be colocated with the CLI script

#### Running as a Frozen Executable (PyInstaller)

When distributed as a PyInstaller-built executable:

- The executable contains the CLI and all modules bundled together
- The `config` directory must be placed next to the executable
- The script detects frozen mode via `sys.frozen` and adjusts paths accordingly

### Expected Filesystem Layout

```
<install_dir>/
├── housekeeping_cli.py (or the frozen executable)
├── config/
│   ├── config_jcl_utilscan.yaml
│   ├── config_cobol_utilscan.yaml
│   └── config_asm_utilscan.yaml
└── modules/
    ├── jcl_utilscan.py
    ├── cobol_utilscan.py
    ├── asm_utilscan.py
    ├── tool_version_report.py
    ├── jcl_convertlog_scanner.py
    ├── cobol_convertlog_scanner.py
    ├── asm_convertlog_scanner.py
    └── ims_analyzer.py
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `AUTOACCEL_OUTPUT_BASE` | Overrides the base output directory | `~/.autoaccel/output` |

### Operating System

The CLI is cross-platform but path examples in this guide use Unix-style paths. On Windows, adjust path separators accordingly (e.g., `C:\Users\<user>\.autoaccel\output`).

[Back to top](#accelerator-tool-usage-guide)

---

## 4. Output Directory Behavior

> **For non-technical readers**: This section explains where the accelerators save their reports. Understanding this helps you (or your team) locate generated files. The key takeaway: by default, reports go to a folder in your home directory called `.autoaccel/output`, organized into subfolders by accelerator type.

### How the Base Output Directory Is Determined

The CLI uses a helper function to create and return the output directory for each accelerator. The logic is:

1. **Check for environment variable**: If `AUTOACCEL_OUTPUT_BASE` is set, use it as the base
2. **Default to home directory**: Otherwise, use `~/.autoaccel/output`
3. **Create per-accelerator subdirectory**: Append the tool-specific folder name (e.g., `jcl_utilities`)

### Concrete Examples

#### Without `AUTOACCEL_OUTPUT_BASE`

```
Base:    /Users/johndoe/.autoaccel/output
JCL:     /Users/johndoe/.autoaccel/output/jcl_utilities
IMS:     /Users/johndoe/.autoaccel/output/ims_analysis
```

#### With `AUTOACCEL_OUTPUT_BASE=/data/reports`

```
Base:    /data/reports
JCL:     /data/reports/jcl_utilities
IMS:     /data/reports/ims_analysis
```

### PyInstaller Behavior

When running as a frozen executable, the CLI also attempts to create an `output` directory next to the executable for portability:

```
<exe_dir>/output/
```

However, the primary output location remains the home directory or environment variable path. The colocated directory is a best-effort fallback that may be useful in portable deployment scenarios.

[Back to top](#accelerator-tool-usage-guide)

---

## 5. Using the CLI: Main Menu Walkthrough

> **For non-technical readers**: This section shows what the tool looks like when you run it. If you're not running it yourself, this gives you an idea of the user experience your technical team will have.

### Launching the CLI

From source:

```bash
python housekeeping_cli.py
```

Or, if distributed as an executable:

```bash
./housekeeping_cli
```

### What You See

```
Automation Accelerator

1. Third Party Utilities Report
2. Factory Tool Version Report
3. Conversion Log Report
4. IMS Analyzer
5. Exit

Enter your choice (1-5):
```

### Main Menu Options

| Choice | Action |
|--------|--------|
| `1` | Opens the Third Party Utilities Report submenu |
| `2` | Runs the Factory Tool Version Report directly |
| `3` | Opens the Conversion Log Report submenu |
| `4` | Runs the IMS Analyzer directly |
| `5` | Exits the CLI |

### Interaction Style

- The CLI is **fully interactive**; it uses `input()` to prompt for choices and paths
- After completing an action, the CLI returns to the relevant menu (or main menu)
- Invalid choices display: `Invalid option. Please select 1, 2, 3, 4, or 5.`
- The loop continues until you select **Exit**

[Back to top](#accelerator-tool-usage-guide)

---

## 6. Accelerator: Third Party Utilities Report

### For Non-Technical Readers

**What this accelerator tells you**: Which third-party software utilities (tools from vendors such as Broadcom/CA, BMC, Syncsort, etc.) are being used in your JCL job streams, COBOL programs, or Assembler code.

**Why it matters**: Over time, applications accumulate dependencies on a mix of in-house tools and external utilities. These dependencies can drive licensing cost, security exposure, and migration complexity. This accelerator **discovers and catalogs those utilities**, turning ad‑hoc job streams and scripts into **structured knowledge** your teams can use for risk reviews, vendor discussions, and modernization planning.

**How to use the output**: Treat the generated report as part of your broader **application knowledge base**. Share it with procurement (for licensing and contract checks), architects (to design replacement strategies for utilities that won't carry forward), and project managers (to size and prioritize migration work that depends on specific third-party tools).

---

### Purpose (Technical)

Scans JCL, COBOL, or Assembler source files to identify references to third-party utilities. This consolidates scattered usage across jobs and programs into a single, searchable view of external dependencies before migration or refactoring.

### Submenu

```
Third Party Utilities Report
1. JCL Utilities Report
2. COBOL Utilities Report
3. Assembler Utilities Report
4. Return to Main Menu

Enter your choice (1-4):
```

---

### 6.1 JCL Utilities Report

#### Module

`modules.jcl_utilscan`

#### Required Configuration File

`config/config_jcl_utilscan.yaml`

This YAML file defines the patterns, utility names, or rules the scanner uses to identify third-party utilities in JCL.

#### Pre-Run Warning

Before execution, the CLI displays:

```
ALERT: Please validate that the YAML configuration file (config_jcl_utilscan.yaml) is correct before proceeding.
Do you want to continue? (Y to proceed, any other key to exit):
```

- Type `Y` (case-insensitive) to proceed
- Any other input cancels and returns to the submenu

#### Output Directory

`<base_output>/jcl_utilities/`

#### Sample Session

```
Third Party Utilities Report
1. JCL Utilities Report
2. COBOL Utilities Report
3. Assembler Utilities Report
4. Return to Main Menu

Enter your choice (1-4): 1
ALERT: Please validate that the YAML configuration file (config_jcl_utilscan.yaml) is correct before proceeding.
Do you want to continue? (Y to proceed, any other key to exit): Y
JCL Utilities Report saved to /Users/johndoe/.autoaccel/output/jcl_utilities
```

#### Error: Missing Config File

```
Required file 'config_jcl_utilscan.yaml' not found in /path/to/config. Please place 'config_jcl_utilscan.yaml' in the config directory.
```

---

### 6.2 COBOL Utilities Report

#### Module

`modules.cobol_utilscan`

#### Required Configuration File

`config/config_cobol_utilscan.yaml`

#### Output Directory

`<base_output>/cobol_utilities/`

#### Sample Session

```
Enter your choice (1-4): 2
COBOL Utilities Report saved to /Users/johndoe/.autoaccel/output/cobol_utilities
```

> **Note**: Unlike the JCL scan, the COBOL and Assembler scans do not display a pre-run confirmation prompt.

#### Error: Missing Config File

```
Required file 'config_cobol_utilscan.yaml' not found in /path/to/config. Please place 'config_cobol_utilscan.yaml' in the config directory.
```

---

### 6.3 Assembler Utilities Report

#### Module

`modules.asm_utilscan`

#### Required Configuration File

`config/config_asm_utilscan.yaml`

#### Output Directory

`<base_output>/asm_utilities/`

#### Sample Session

```
Enter your choice (1-4): 3
Assembler Utilities Report saved to /Users/johndoe/.autoaccel/output/asm_utilities
```

#### Error: Missing Config File

```
Required file 'config_asm_utilscan.yaml' not found in /path/to/config. Please place 'config_asm_utilscan.yaml' in the config directory.
```

[Back to top](#accelerator-tool-usage-guide)

---

## 7. Accelerator: Factory Tool Version Report

### For Non-Technical Readers

**What this accelerator tells you**: An inventory of all tools installed in a specific directory, along with their version numbers.

**Why it matters**: During modernization, you need consistent tooling across environments. This report helps verify that development, test, and production environments have the same tool versions—and helps identify outdated or missing tools that could cause problems. It supports environment readiness checks before modernization and provides audit/compliance evidence.

**How to use the output**: Share the Excel report with environment managers, DevOps teams, or vendors to validate environment readiness. Compare reports from different environments (dev, test, prod) to ensure consistency. Use as evidence for audit and compliance reviews.

---

### Purpose (Technical)

Scans a directory containing factory tools and produces an Excel report documenting which tools are present and their versions. Useful for environment audits and migration planning.

### Module

`modules.tool_version_report`

### Flow

1. CLI creates the output directory: `<base_output>/tool_versions/`
2. User is prompted for:
   - **Tools directory path**: The folder to scan (e.g., `D:/factory/tools`)
   - **Application name**: A prefix for the output file (e.g., `myapp`)
3. The module scans the directory and writes the report
4. A summary is displayed on screen

### Prompts

```
Running Factory Tool Version Report...

Please enter the full path to your tools directory (e.g. D:/factory/tools): /opt/factory/tools
Please enter an application name to prefix the report file (e.g. myapp): clientxyz
```

### Output

- **File**: `<app_name>_tools_report.xlsx`
- **Location**: `<base_output>/tool_versions/`
- **Example**: `/Users/johndoe/.autoaccel/output/tool_versions/clientxyz_tools_report.xlsx`

### On-Screen Display

After generating the report, `display_selected_tools(df)` prints a subset of the discovered tools to the terminal for quick review.

### Sample Session

```
Automation Accelerator

1. Third Party Utilities Report
2. Factory Tool Version Report
3. Conversion Log Report
4. IMS Analyzer
5. Exit

Enter your choice (1-5): 2

Running Factory Tool Version Report...

Please enter the full path to your tools directory (e.g. D:/factory/tools): /opt/factory/tools
Please enter an application name to prefix the report file (e.g. myapp): acme

[On-screen tool summary displayed here]
```

[Back to top](#accelerator-tool-usage-guide)

---

## 8. Accelerator: Conversion Log Report

### For Non-Technical Readers

**What this accelerator tells you**: A structured summary of what happened during code conversion—including errors, warnings, and statistics—extracted from verbose log files.

**Why it matters**: Conversion tools generate lengthy, technical log files that are difficult to review manually. This accelerator **turns those scattered log messages into a focused, filterable report**, making it far easier to **pinpoint root causes** of failures and understand the overall health of your conversion pipeline.

**How to use the output**: Use the Excel report in status meetings to show conversion progress. Filter by error type to prioritize fixes. Share with stakeholders to demonstrate quality metrics or identify blockers. Track conversion quality trends over time to support delivery pipelines with confidence.

---

### Purpose (Technical)

Parses conversion log files generated during mainframe-to-target migrations and produces structured Excel reports. This **consolidates scattered diagnostic data** from verbose logs, helping teams quickly identify errors, warnings, and statistics without manual analysis.

### Submenu

```
Conversion Log Report
1. JCL Conversion Log Report
2. COBOL Conversion Log Report
3. Assembler Conversion Log Report
4. Return to Main Menu

Enter your choice (1-4):
```

---

### 8.1 JCL Conversion Log Report

#### For Non-Technical Readers

**What this accelerator tells you**: A structured view of what happened when JCL (Job Control Language) jobs were processed by your conversion or modernization tools—how many jobs ran cleanly, which ones failed, and what types of issues were detected.

**Why it matters**: Raw JCL conversion logs are long and technical. This accelerator **turns those scattered log messages into a focused, filterable report**, making it far easier to **pinpoint root causes** of failures and understand the overall health of your conversion pipeline.

**How to use the output**: Use the Excel report to monitor conversion progress and stability. Filter by error or warning type to identify systemic problems (for example, missing procedures or unsupported utilities). Bring the summarized metrics into status meetings or dashboards to show where work is needed and how quality is trending over time.

#### Module

`modules.jcl_convertlog_scanner`

#### Input

User is prompted for the full path to a JCL conversion log file:

```
Enter the full path to the JCL conversion log file: /logs/jcl_convert.log
```

#### File Existence Check

If the file does not exist:

```
Error: Log file /logs/jcl_convert.log not found!
```

The CLI then returns to the submenu for another attempt.

#### Output Directory

`<base_output>/jcl_conversion_logs/`

#### How It Works

The CLI manipulates `sys.argv` to pass the log file path and output directory to the module's `main()` function:

```python
sys.argv = [sys.argv[0], log_file_path, "--output-dir", output_dir]
jclscanner.main()
```

After execution, `sys.argv` is reset to avoid side effects.

#### Sample Session

```
Enter your choice (1-4): 1
Enter the full path to the JCL conversion log file: /data/logs/jcl_migration.log
JCL Conversion Log Analysis completed. Report saved to /Users/johndoe/.autoaccel/output/jcl_conversion_logs
```

---

### 8.2 COBOL Conversion Log Report

#### For Non-Technical Readers

**What this accelerator tells you**: A structured summary of what happened when COBOL code was passed through an automated conversion or modernization tool—how many components succeeded, which ones failed, and what types of issues were detected.

**Why it matters**: Conversion tools often produce long, highly technical log files that are difficult to read. This accelerator **turns that scattered diagnostic data into a focused, navigable report**, making it much easier to **pinpoint root causes** of failed conversions, track progress over time, and keep modernization pipelines moving with confidence.

**How to use the output**: Use the Excel report to support status meetings, steering committees, and defect triage. Filter by error or warning type to prioritize work. Combine multiple reports over time to show how your conversion quality is improving as issues are resolved.

#### Module

`modules.cobol_convertlog_scanner`

#### Input

```
Enter the full path to the COBOL conversion log file: /logs/cobol_convert.log
```

#### File Existence Check

Same behavior as JCL: error message and return to submenu if file not found.

#### Output Directory

`<base_output>/cobol_conversion_logs/`

#### How It Works

Unlike JCL and ASM, the COBOL scanner is called directly without `sys.argv` manipulation:

```python
cobolscanner.create_excel_report(log_file_path, output_dir)
```

#### Sample Session

```
Enter your choice (1-4): 2
Enter the full path to the COBOL conversion log file: /data/logs/cobol_migration.log
COBOL Conversion Log Analysis completed. Report saved to /Users/johndoe/.autoaccel/output/cobol_conversion_logs
```

---

### 8.3 Assembler Conversion Log Report

#### For Non-Technical Readers

**What this accelerator tells you**: A summarized view of how Assembler programs fared when they were put through automated conversion or analysis tools—showing which programs converted successfully, which did not, and the key issues reported.

**Why it matters**: Assembler code is often some of the most complex and least understood logic in a mainframe estate. Its conversion logs can be especially dense. This accelerator **consolidates that low-level diagnostic information into an accessible report**, helping teams **identify patterns and root causes** behind failed conversions and quantify the complexity of Assembler migration.

**How to use the output**: Share the report with technical leads and architects to prioritize which Assembler components need attention first. Use it to estimate remediation effort, plan sequencing (e.g., tackle the highest-error modules early), and communicate Assembler-related risk to stakeholders.

#### Module

`modules.asm_convertlog_scanner`

#### Input

```
Enter the full path to the Assembler conversion log file: /logs/asm_convert.log
```

#### File Existence Check

Same behavior as JCL and COBOL.

#### Output Directory

`<base_output>/asm_conversion_logs/`

#### How It Works

Like the JCL scanner, the ASM scanner uses `sys.argv` manipulation:

```python
sys.argv = [sys.argv[0], log_file_path, "--output-dir", output_dir]
asmscanner.main()
```

#### Sample Session

```
Enter your choice (1-4): 3
Enter the full path to the Assembler conversion log file: /data/logs/asm_migration.log
Assembler Conversion Log Analysis completed. Report saved to /Users/johndoe/.autoaccel/output/asm_conversion_logs
```

[Back to top](#accelerator-tool-usage-guide)

---

## 9. Accelerator: IMS Analyzer

### For Non-Technical Readers

**What this accelerator tells you**: Which programs use IMS (IBM's hierarchical database system), what types of database calls they make, and how complex the IMS usage is across your codebase.

**Why it matters**: IMS is one of the most complex components to migrate from mainframes. Understanding how extensively your applications depend on IMS—and which specific features they rely on—is critical for estimating IMS migration complexity, prioritizing work, and supporting architecture decisions on database strategies.

**How to use the output**: Share the IMS Impact Report with database architects, migration planners, and project leadership. Use it to prioritize which programs to tackle first, estimate the complexity of database conversion work, and identify programs that may need significant refactoring. The structured data supports architecture documentation and feeds into modernization planning discussions.

---

### Purpose (Technical)

Analyzes COBOL programs, COBOL copybooks, and Assembler listings to identify IMS-related API calls, parameters, and functions. Produces an impact report useful for understanding IMS dependencies before migration or refactoring.

### Module

`modules.ims_analyzer`

### Output Directory

`<base_output>/ims_analysis/`

### Prompts

The user must provide three folder paths:

```
Enter the path to the COBOL programs folder: /src/cobol
Enter the path to the COBOL Copybooks folder: /src/copybooks
Enter the path to the ASM (Assembler listing) folder: /src/asm
```

### Validation

If any path is blank:

```
All folder paths are required.
```

The CLI then returns to the main menu.

### Processing

The module performs two main operations:

1. **Scan**: `scan_all(cobol_folder, copybook_folder, asm_folder)` returns:
   - `summary_data`: High-level summary of IMS usage
   - `call_inventory`: Detailed inventory of IMS calls
   - `param_counts`: Parameter usage statistics
   - `function_counts`: Function usage statistics

2. **Report Generation**: `generate_final_excel_report_with_clean_params(...)` writes an Excel report to the output directory

### Output

- **File**: `IMS_Impact_Report.xlsx`
- **Location**: `<base_output>/ims_analysis/`
- **Example**: `/Users/johndoe/.autoaccel/output/ims_analysis/IMS_Impact_Report.xlsx`

### Sample Session

```
Automation Accelerator

1. Third Party Utilities Report
2. Factory Tool Version Report
3. Conversion Log Report
4. IMS Analyzer
5. Exit

Enter your choice (1-5): 4
Running IMS Analyzer...
Enter the path to the COBOL programs folder: /projects/legacy/cobol
Enter the path to the COBOL Copybooks folder: /projects/legacy/copybooks
Enter the path to the ASM (Assembler listing) folder: /projects/legacy/asm
IMS Analysis Report saved to /Users/johndoe/.autoaccel/output/ims_analysis
```

### Example Folder Layout

```
/projects/legacy/
├── cobol/
│   ├── PROG001.cbl
│   ├── PROG002.cbl
│   └── ...
├── copybooks/
│   ├── CPYBK01.cpy
│   ├── CPYBK02.cpy
│   └── ...
└── asm/
    ├── ASMPGM1.asm
    ├── ASMPGM2.asm
    └── ...
```

[Back to top](#accelerator-tool-usage-guide)

---

## 10. Configuration Files and Customization

> **For non-technical readers**: Some accelerators need configuration files that tell them where to look and what to look for. If you're not running the tools yourself, your technical team handles these files. The key point: if an accelerator fails with a "config file not found" error, it means the setup is incomplete—ask your technical team to check the `config` folder.

### Overview

Three accelerators require YAML configuration files:

| Accelerator | Config File |
|-------------|-------------|
| JCL Utilities Report | `config_jcl_utilscan.yaml` |
| COBOL Utilities Report | `config_cobol_utilscan.yaml` |
| Assembler Utilities Report | `config_asm_utilscan.yaml` |

### Location

All configuration files must be placed in a `config` directory located:

- **From source**: Next to the CLI script (e.g., `src/automationaccelerator/config/`)
- **Frozen executable**: Next to the executable file

### What They Control

These YAML files typically define:

- **Scan paths**: Directories containing source files to analyze
- **Utility patterns**: Names or patterns of third-party utilities to detect
- **Exclusion rules**: Files or patterns to skip
- **Output preferences**: Report formatting options

> **Note**: The exact keys and structure depend on each module's implementation. Refer to sample config files provided with the distribution or module documentation for specifics.

### Missing Config File Error

If a required config file is not found, the CLI displays:

```
Required file '<config_name>' not found in <config_dir>. Please place '<config_name>' in the config directory.
```

The operation is cancelled and the CLI returns to the submenu.

### Optional: Output Directory Injection

If a module supports it (via `add_output_dir_to_config`), the CLI injects the output directory path into the loaded configuration before processing.

[Back to top](#accelerator-tool-usage-guide)

---

## 11. End-to-End Usage Examples

These scenarios walk through common use cases from start to finish. Each includes guidance on who typically uses the scenario and how the output supports decision-making.

---

### Scenario 1: Identify Third-Party Utilities in JCL

**Who should use this**: Architects, procurement leads, project managers, migration engineers.

**Goal**: Understand which third-party utilities are used across your JCL job streams.

**Steps**:

1. Ensure `config_jcl_utilscan.yaml` is configured with your JCL source paths and utility patterns
2. Launch the CLI
3. Select `1` (Third Party Utilities Report)
4. Select `1` (JCL Utilities Report)
5. Confirm by typing `Y`

**Output**: Report in `~/.autoaccel/output/jcl_utilities/`

**Using the output in practice**: Open the Excel report and review the list of detected utilities. Share with procurement to validate licensing requirements and negotiate contracts. Share with architects to identify utilities that need replacement strategies for the target platform. Include utility counts in project planning documents to justify scope and budget. Use in vendor discussions to understand migration tool requirements and compatibility.

---

### Scenario 2: Analyze COBOL Conversion Logs

**Who should use this**: Engineers, QA leads, project managers tracking conversion progress.

**Goal**: Parse a COBOL conversion log and produce a structured Excel report of issues.

**Steps**:

1. Launch the CLI
2. Select `3` (Conversion Log Report)
3. Select `2` (COBOL Conversion Log Report)
4. Enter the full path to your log file: `/data/logs/cobol_convert_20231215.log`

**Output**: Excel report in `~/.autoaccel/output/cobol_conversion_logs/`

**Using the output in practice**: Filter the Excel report by severity (errors vs. warnings) to prioritize fixes. Use summary statistics in status reports to show conversion progress over time. Identify patterns in failures to address systemic issues. Present metrics in steering committee meetings to demonstrate quality trends and justify resource allocation for remediation work.

---

### Scenario 3: Assess IMS Impact

**Who should use this**: Database architects, migration planners, project leadership, technical leads.

**Goal**: Understand IMS API usage across COBOL programs and Assembler listings.

**Steps**:

1. Launch the CLI
2. Select `4` (IMS Analyzer)
3. Enter paths:
   - COBOL programs: `/app/src/cobol`
   - Copybooks: `/app/src/copy`
   - ASM listings: `/app/src/asm`

**Output**: `IMS_Impact_Report.xlsx` in `~/.autoaccel/output/ims_analysis/`

**Using the output in practice**: Review the summary sheet for overall IMS complexity. Identify programs with the highest IMS call counts for prioritization. Share with database architects to plan the IMS-to-target-database migration approach. Use the data in steering committee presentations to explain database migration complexity and justify specialized resources. Feed the structured data into architecture documentation and migration wave planning.

---

### Scenario 4: Audit Factory Tool Versions

**Who should use this**: Environment managers, DevOps teams, compliance officers, project managers.

**Goal**: Document which tools and versions are installed in a factory environment.

**Steps**:

1. Launch the CLI
2. Select `2` (Factory Tool Version Report)
3. Enter the tools directory: `/opt/factory/tools`
4. Enter an application name: `prodenv`

**Output**: `prodenv_tools_report.xlsx` in `~/.autoaccel/output/tool_versions/`

**Using the output in practice**: Compare reports from different environments (dev, test, prod) to ensure consistency and identify discrepancies. Use as evidence for audit and compliance reviews. Share with vendors to validate tooling requirements are met before major deployments. Include in environment readiness assessments and handover documentation.

[Back to top](#accelerator-tool-usage-guide)

---

## 12. Troubleshooting and Common Pitfalls

> **For non-technical readers**: This section helps when things go wrong. Even if you're not running the tools yourself, understanding these common issues helps you communicate with your technical team. For each problem, we explain what the error means and what action to take—or what to ask your team to check.

### Missing Configuration Files

**Symptom**:

```
Required file 'config_jcl_utilscan.yaml' not found in /path/to/config.
```

**Resolution**: Place the required YAML file in the `config` directory next to the CLI script or executable.

**For non-technical stakeholders**: If you see this error reported, ask your technical team: "Is the `config` folder set up correctly next to the tool? Does it contain the required YAML files?"

---

### Invalid Log File Path

**Symptom**:

```
Error: Log file /nonexistent/path.log not found!
```

**Resolution**: Verify the file path is correct and the file exists. The CLI returns to the submenu so you can re-enter the path.

**For non-technical stakeholders**: This means the tool couldn't find the log file at the location provided. Ask your team: "Is the file path correct? Does the file exist at that location?"

---

### Permission Issues with Output Directory

**Symptom**: The CLI fails silently or reports an error when trying to save reports.

**Resolution**:

- Check write permissions on `~/.autoaccel/output/` or your custom `AUTOACCEL_OUTPUT_BASE`
- If using a frozen executable, ensure the user has write access to the fallback `<exe_dir>/output/` directory

**For non-technical stakeholders**: If reports aren't being generated, the tool may not have permission to write files. Ask your team: "Does the user running the tool have write access to the output folder?"

---

### Confusion About Output Location

**Symptom**: You can't find your generated reports.

**Resolution**:

1. Check if `AUTOACCEL_OUTPUT_BASE` is set in your environment:
   ```bash
   echo $AUTOACCEL_OUTPUT_BASE
   ```
2. If not set, look in `~/.autoaccel/output/`
3. Reports are in tool-specific subdirectories (e.g., `jcl_utilities`, `ims_analysis`)

---

### Running in Automated/CI Environments

The CLI is interactive and uses `input()`, which makes direct automation challenging.

**Workarounds**:

- Pipe input from a file or use `expect` scripts
- Import modules directly and call their functions programmatically
- Consider wrapping the CLI or refactoring to support command-line arguments

---

### Source vs. Frozen Behavior

| Aspect | From Source | Frozen (PyInstaller) |
|--------|-------------|----------------------|
| Config location | Next to script | Next to executable |
| Module imports | Via `PYTHONPATH` or package | Bundled in executable |
| Fallback output | Not created | `<exe_dir>/output/` attempted |

[Back to top](#accelerator-tool-usage-guide)

---

## 13. Reference: Menu Map and Modules

This quick-reference table maps each menu option to its corresponding module, output location, and typical output file. Use this as a lookup when you need to quickly identify what runs where.

| Main Menu | Submenu | Module | Output Directory | Output Artifact |
|-----------|---------|--------|------------------|-----------------|
| 1. Third Party Utilities Report | 1. JCL Utilities Report | `modules.jcl_utilscan` | `jcl_utilities` | Report (format per module) |
| | 2. COBOL Utilities Report | `modules.cobol_utilscan` | `cobol_utilities` | Report (format per module) |
| | 3. Assembler Utilities Report | `modules.asm_utilscan` | `asm_utilities` | Report (format per module) |
| 2. Factory Tool Version Report | — | `modules.tool_version_report` | `tool_versions` | `<app>_tools_report.xlsx` |
| 3. Conversion Log Report | 1. JCL Conversion Log Report | `modules.jcl_convertlog_scanner` | `jcl_conversion_logs` | Excel report |
| | 2. COBOL Conversion Log Report | `modules.cobol_convertlog_scanner` | `cobol_conversion_logs` | Excel report |
| | 3. Assembler Conversion Log Report | `modules.asm_convertlog_scanner` | `asm_conversion_logs` | Excel report |
| 4. IMS Analyzer | — | `modules.ims_analyzer` | `ims_analysis` | `IMS_Impact_Report.xlsx` |
| 5. Exit | — | — | — | — |

[Back to top](#accelerator-tool-usage-guide)

---

## Appendix: Quick Reference Card

Use this appendix as a quick lookup for the most commonly needed information.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTOACCEL_OUTPUT_BASE` | `~/.autoaccel/output` | Base directory for all output |

### Config Files Required

| File | Used By |
|------|---------|
| `config_jcl_utilscan.yaml` | JCL Utilities Report |
| `config_cobol_utilscan.yaml` | COBOL Utilities Report |
| `config_asm_utilscan.yaml` | Assembler Utilities Report |

### Menu Navigation

- Enter `5` at main menu to exit
- Enter `4` at any submenu to return to main menu

### Default Output Location

If `AUTOACCEL_OUTPUT_BASE` is not set:

```
~/.autoaccel/output/
├── jcl_utilities/
├── cobol_utilities/
├── asm_utilities/
├── tool_versions/
├── jcl_conversion_logs/
├── cobol_conversion_logs/
├── asm_conversion_logs/
└── ims_analysis/
```

[Back to top](#accelerator-tool-usage-guide)

---

*End of Accelerator Tool Usage Guide*
