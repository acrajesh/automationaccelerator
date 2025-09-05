#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ADRDSSU Impact Analyzer

This tool analyzes JCL utilities report Excel files and cross-references ADRDSSU usage
with metadata from YAML files to determine support status of options/clauses.
It generates a comprehensive report showing impact analysis and support status.
"""

import os
import re
import yaml
import pandas as pd
import logging
from datetime import datetime
import xlsxwriter
from pathlib import Path
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ADRDSSUImpactAnalyzer:
    """
    Analyzes ADRDSSU usage in JCL and generates impact analysis reports
    """
    
    def __init__(self, yaml_path, excel_report_path, output_dir=None):
        """
        Initialize the analyzer with paths to input files and output directory
        
        Args:
            yaml_path (str): Path to ADRDSSU metadata YAML file
            excel_report_path (str): Path to JCL utilities report Excel file
            output_dir (str, optional): Directory for output files. Defaults to same directory as excel_report_path.
        """
        self.yaml_path = yaml_path
        self.excel_report_path = excel_report_path
        
        if output_dir is None:
            self.output_dir = os.path.dirname(excel_report_path)
        else:
            self.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
            
        self.metadata = None
        self.adrdssu_data = None
        self.analysis_results = {
            'statements': {},
            'options': {},
            'job_references': {},
            'summary': {
                'supported': 0,
                'not_supported': 0,
                'accepted_but_ignored': 0,
                'unknown': 0,
                'total': 0
            }
        }
        
    def load_metadata(self):
        """Load and parse the ADRDSSU metadata YAML file"""
        try:
            with open(self.yaml_path, 'r') as file:
                self.metadata = yaml.safe_load(file)
                logger.info(f"Loaded metadata from {self.yaml_path}")
                return True
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            return False
    
    def load_excel_report(self):
        """Load the JCL utilities report Excel file and extract ADRDSSU data"""
        try:
            # Check if ADRDSSU sheet exists in the Excel file
            excel_file = pd.ExcelFile(self.excel_report_path)
            if 'ADRDSSU' not in excel_file.sheet_names:
                logger.error(f"ADRDSSU sheet not found in {self.excel_report_path}")
                return False
            
            # Load the ADRDSSU sheet
            self.adrdssu_data = pd.read_excel(self.excel_report_path, sheet_name='ADRDSSU')
            logger.info(f"Loaded ADRDSSU data from {self.excel_report_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading Excel report: {str(e)}")
            return False
    
    def extract_statement_type(self, content):
        """
        Extract the statement type from ADRDSSU control card or step content
        
        Args:
            content (str): Control card content or step content
            
        Returns:
            str: Statement type (COPY DATASET, DUMP, RESTORE, etc.) or None if not found
        """
        # Common ADRDSSU statement types
        statement_types = [
            'COPY DATASET', 'COPYDUMP', 'DUMP', 'RESTORE'
        ]
        
        if pd.isna(content) or not content:
            return None
            
        content = content.upper()
        
        for stmt_type in statement_types:
            if stmt_type in content:
                return stmt_type
                
        return None
    
    def extract_options(self, content, statement_type):
        """
        Extract options/clauses from ADRDSSU control card or step content
        
        Args:
            content (str): Control card content or step content
            statement_type (str): Statement type (COPY DATASET, DUMP, RESTORE, etc.)
            
        Returns:
            list: List of options found in the content
        """
        if pd.isna(content) or not content or statement_type is None:
            return []
            
        content = content.upper()
        options = []
        
        # Get all supported, not supported, and accepted but ignored options for this statement type
        all_options = []
        if statement_type in self.metadata['ADRDSSU']['Statements']:
            stmt_metadata = self.metadata['ADRDSSU']['Statements'][statement_type]
            all_options.extend(stmt_metadata.get('Supported', []))
            all_options.extend(stmt_metadata.get('Not supported', []))
            all_options.extend(stmt_metadata.get('Accepted but ignored', []))
        
        # Look for each option in the content
        for option in all_options:
            # Handle special case for DATASET options which may have different formats
            if option.startswith('DATASET('):
                option_base = option[8:-1]  # Extract what's inside DATASET()
                patterns = [
                    rf'\bDATASET\s*\(\s*{option_base}\s*\)',
                    rf'\bDSN\s*\(\s*{option_base}\s*\)',
                    rf'\bDATA\s*\(\s*{option_base}\s*\)'
                ]
                for pattern in patterns:
                    if re.search(pattern, content):
                        options.append(option)
                        break
            else:
                # For regular options, just check if they appear as words
                if re.search(rf'\b{option}\b', content):
                    options.append(option)
        
        return options
    
    def determine_option_status(self, option, statement_type):
        """
        Determine the support status of an option for a given statement type
        
        Args:
            option (str): Option name
            statement_type (str): Statement type (COPY DATASET, DUMP, RESTORE, etc.)
            
        Returns:
            str: Status ('Supported', 'Not supported', 'Accepted but ignored', or 'Unknown')
        """
        if statement_type not in self.metadata['ADRDSSU']['Statements']:
            return 'Unknown'
            
        stmt_metadata = self.metadata['ADRDSSU']['Statements'][statement_type]
        
        if option in stmt_metadata.get('Supported', []):
            return 'Supported'
        elif option in stmt_metadata.get('Not supported', []):
            return 'Not supported'
        elif option in stmt_metadata.get('Accepted but ignored', []):
            return 'Accepted but ignored'
        else:
            return 'Unknown'
    
    def analyze_data(self):
        """Analyze the ADRDSSU data and cross-reference with metadata"""
        if self.metadata is None or self.adrdssu_data is None:
            logger.error("Metadata or ADRDSSU data not loaded")
            return False
        
        # Initialize counters
        total_options = 0
        supported_options = 0
        not_supported_options = 0
        accepted_but_ignored_options = 0
        unknown_options = 0
        
        # Process each row in the ADRDSSU data
        for _, row in self.adrdssu_data.iterrows():
            file_name = row.get('File Name', '')
            step_name = row.get('Step Name', '')
            step_content = row.get('Step', '')
            sysin_type = row.get('SYSIN Type', '')
            sysin_statement = row.get('SYSIN Statement', '')
            control_card_content = row.get('Control Card Content', '')
            
            # Create a unique reference for this job/step
            job_ref = f"{file_name} - {step_name}"
            
            # Combine all content for analysis
            all_content = []
            if not pd.isna(step_content) and step_content:
                all_content.append(step_content)
            if not pd.isna(sysin_statement) and sysin_statement:
                all_content.append(sysin_statement)
            if not pd.isna(control_card_content) and control_card_content:
                all_content.append(control_card_content)
                
            combined_content = "\n".join(all_content)
            
            # Extract statement type
            statement_type = self.extract_statement_type(combined_content)
            if statement_type is None:
                logger.warning(f"Could not determine statement type for {job_ref}")
                continue
                
            # Extract options
            options = self.extract_options(combined_content, statement_type)
            
            # Track statement usage
            if statement_type not in self.analysis_results['statements']:
                self.analysis_results['statements'][statement_type] = {
                    'count': 0,
                    'jobs': []
                }
            self.analysis_results['statements'][statement_type]['count'] += 1
            self.analysis_results['statements'][statement_type]['jobs'].append(job_ref)
            
            # Process each option
            for option in options:
                status = self.determine_option_status(option, statement_type)
                
                # Update counters
                total_options += 1
                if status == 'Supported':
                    supported_options += 1
                elif status == 'Not supported':
                    not_supported_options += 1
                elif status == 'Accepted but ignored':
                    accepted_but_ignored_options += 1
                else:
                    unknown_options += 1
                
                # Track option usage
                if option not in self.analysis_results['options']:
                    self.analysis_results['options'][option] = {
                        'count': 0,
                        'status': status,
                        'statement_types': set(),
                        'jobs': []
                    }
                self.analysis_results['options'][option]['count'] += 1
                self.analysis_results['options'][option]['statement_types'].add(statement_type)
                self.analysis_results['options'][option]['jobs'].append(job_ref)
                
                # Track job references
                if job_ref not in self.analysis_results['job_references']:
                    self.analysis_results['job_references'][job_ref] = {
                        'statement_type': statement_type,
                        'options': {}
                    }
                self.analysis_results['job_references'][job_ref]['options'][option] = status
        
        # Update summary
        self.analysis_results['summary'] = {
            'supported': supported_options,
            'not_supported': not_supported_options,
            'accepted_but_ignored': accepted_but_ignored_options,
            'unknown': unknown_options,
            'total': total_options
        }
        
        logger.info(f"Analysis complete. Found {total_options} option usages across {len(self.analysis_results['job_references'])} jobs.")
        return True
    
    def generate_excel_report(self):
        """Generate Excel report with impact analysis results"""
        if not self.analysis_results['options']:
            logger.error("No analysis results to report")
            return False
            
        # Create output directory if it doesn't exist
        output_dir = Path(self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine next version number
        version = self._get_next_version_number()
        output_file = output_dir / f"adrdssu_impact_analysis_v{version}.xlsx"
        
        logger.info(f"Generating Excel report: {output_file}")
        
        try:
            # Create Excel writer with xlsxwriter engine
            writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
            
            # Create formats for Excel cells - match jcl_utilscan style
            workbook = writer.book
            header_format = workbook.add_format({
                'bold': True, 
                'bg_color': '#D7E4BC',
                'text_wrap': True,
                'valign': 'top',
                'font_size': 9
            })
            wrap_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'font_size': 9
            })
            
            # Create formats for status colors
            supported_format = workbook.add_format({
                'bg_color': '#92D050',  # Bright green
                'text_wrap': True,
                'valign': 'top',
                'font_size': 9
            })
            not_supported_format = workbook.add_format({
                'bg_color': '#FF0000',  # Bright red
                'text_wrap': True,
                'valign': 'top',
                'font_size': 9
            })
            accepted_format = workbook.add_format({
                'bg_color': '#FFC000',  # Bright yellow/orange
                'text_wrap': True,
                'valign': 'top',
                'font_size': 9
            })
            unknown_format = workbook.add_format({
                'bg_color': '#A5A5A5',  # Darker gray
                'text_wrap': True,
                'valign': 'top',
                'font_size': 9
            })
            
            # Create Dashboard sheet
            summary = self.analysis_results['summary']
            total = summary['total'] if summary['total'] > 0 else 1  # Avoid division by zero
            
            # Count unique options by status
            unique_options = {
                'supported': len([opt for opt, data in self.analysis_results['options'].items() 
                                if data['status'] == 'Supported']),
                'not_supported': len([opt for opt, data in self.analysis_results['options'].items() 
                                    if data['status'] == 'Not supported']),
                'accepted_but_ignored': len([opt for opt, data in self.analysis_results['options'].items() 
                                          if data['status'] == 'Accepted but ignored']),
                'unknown': len([opt for opt, data in self.analysis_results['options'].items() 
                              if data['status'] == 'Unknown']),
            }
            unique_total = sum(unique_options.values())
            
            # First dashboard table - Status breakdown
            dashboard_data = [
                ['Utility', 'Supported Unique Count', 'Supported Unique %', 
                 'Accepted but Ignored Unique Count', 'Accepted but Ignored Unique %', 
                 'Not Supported Unique Count', 'Not Supported Unique %'],
                ['ADRDSSU', 
                 unique_options['supported'], f"{unique_options['supported']/unique_total*100:.2f}%", 
                 unique_options['accepted_but_ignored'], f"{unique_options['accepted_but_ignored']/unique_total*100:.2f}%", 
                 unique_options['not_supported'], f"{unique_options['not_supported']/unique_total*100:.2f}%"]
            ]
            
            # Second dashboard table - Summary statistics
            addressed_options = unique_options['supported'] + unique_options['accepted_but_ignored']
            pending_options = unique_options['not_supported']
            pending_percentage = (pending_options / unique_total * 100) if unique_total > 0 else 0
            
            summary_data = [
                ['Utility', 'Total Unique Options', 'Solution Available', 'Solution Available %', 'Options Pending', 'Options Pending %'],
                ['ADRDSSU', unique_total, addressed_options, f"{(addressed_options/unique_total*100):.1f}%", pending_options, f"{pending_percentage:.1f}%"]
            ]
            
            df_dashboard = pd.DataFrame(dashboard_data[1:], columns=dashboard_data[0])
            df_dashboard.to_excel(writer, sheet_name='Dashboard', index=False)
            
            # Format Dashboard sheet
            worksheet = writer.sheets['Dashboard']
            for col_num, value in enumerate(df_dashboard.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Apply formatting to data rows
            for row_num in range(len(df_dashboard)):
                for col_num in range(len(df_dashboard.columns)):
                    worksheet.write(row_num + 1, col_num, df_dashboard.iloc[row_num, col_num], wrap_format)
            
            # Add space between tables
            worksheet.write(len(df_dashboard) + 2, 0, '', wrap_format)
            
            # Add second summary table
            for col_num, value in enumerate(summary_data[0]):
                worksheet.write(len(df_dashboard) + 3, col_num, value, header_format)
            
            for row_num, row in enumerate(summary_data[1:]):
                for col_num, value in enumerate(row):
                    worksheet.write(len(df_dashboard) + 4 + row_num, col_num, value, wrap_format)
            
            # Adjust column widths for dashboard - ensure consistent width and proper wrapping
            column_widths = [20, 20, 15, 20, 15, 20, 15, 20]  # Widths for each column in dashboard
            for i, width in enumerate(column_widths):
                if i < max(len(dashboard_data[0]), len(summary_data[0])):
                    worksheet.set_column(i, i, width)
                    
            # Set row heights for better readability
            for row_num in range(1, len(df_dashboard) + 1):
                worksheet.set_row(row_num, 30)  # Set consistent row height
                
            # Set row heights for summary table
            for row_num in range(len(df_dashboard) + 3, len(df_dashboard) + 5):
                worksheet.set_row(row_num, 30)  # Set consistent row height
            
            # Statement Summary sheet is removed as requested
            
            # Create Options Analysis sheet
            option_rows = []
            for option, details in self.analysis_results['options'].items():
                statement_types = ', '.join(sorted(details['statement_types']))
                reference_jobs = sorted(set(details['jobs']))
                if len(reference_jobs) > 2:
                    reference_jobs = reference_jobs[:2]
                reference_jobs_str = ', '.join(reference_jobs)
                option_rows.append([option, statement_types, details['status'], reference_jobs_str])
                
            df_options = pd.DataFrame(option_rows, columns=[
                'Option', 
                'Statement Types',
                'Status', 
                'Reference Jobs'
            ])
            df_options.to_excel(writer, sheet_name='Options Analysis', index=False)
            
            # Format Options Analysis sheet
            worksheet = writer.sheets['Options Analysis']
            for col_num, value in enumerate(df_options.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Apply formatting to options data
            for row_num, row in enumerate(df_options.itertuples(index=False)):
                for col_num, value in enumerate(row):
                    if col_num == 2:  # Status column (now in column C)
                        if row[2] == 'Supported':
                            worksheet.write(row_num + 1, col_num, row[2], supported_format)
                        elif row[2] == 'Not supported':
                            worksheet.write(row_num + 1, col_num, row[2], not_supported_format)
                        elif row[2] == 'Accepted but ignored':
                            worksheet.write(row_num + 1, col_num, row[2], accepted_format)
                        else:
                            worksheet.write(row_num + 1, col_num, row[2], unknown_format)
                    else:
                        worksheet.write(row_num + 1, col_num, row[col_num], wrap_format)
            
            # Adjust column widths to match jcl_utilscan style
            column_widths = [30, 20, 30, 50]  # Widths for Option, Status, Statement Types, Sample Jobs
            for i, width in enumerate(column_widths):
                worksheet.set_column(i, i, width)
                
            # Set consistent row heights for better readability and to ensure text is visible without double-clicking
            for row_num in range(1, len(df_options) + 1):
                # Calculate appropriate row height based on content
                max_text_lines = 1
                for col_idx, col_name in enumerate(df_options.columns):
                    if pd.notna(df_options.iloc[row_num-1, col_idx]):
                        text = str(df_options.iloc[row_num-1, col_idx])
                        # Estimate number of lines based on text length and column width
                        estimated_lines = max(1, len(text) // (column_widths[col_idx] * 2) + text.count('\n') + 1)
                        max_text_lines = max(max_text_lines, estimated_lines)
                
                # Set row height (16 points per line of text, with a minimum of 25)
                row_height = max(25, max_text_lines * 16)
                worksheet.set_row(row_num, row_height)
            
            # Create Job References sheet with risk assessment
            job_rows = []
            for job_ref, data in self.analysis_results['job_references'].items():
                # Count options by status for this job
                status_counts = {'Supported': 0, 'Not supported': 0, 'Accepted but ignored': 0, 'Unknown': 0}
                unknown_options = []
                for option, status in data['options'].items():
                    status_counts[status] += 1
                    if status == 'Unknown':
                        unknown_options.append(option)
                
                # Calculate risk level based on unsupported options
                if status_counts['Not supported'] > 0:
                    risk_level = 'High'
                elif status_counts['Unknown'] > 0:
                    risk_level = 'Medium'
                elif status_counts['Accepted but ignored'] > 0:
                    risk_level = 'Low'
                else:
                    risk_level = 'None'
                
                # Create a summary string of options by status
                options_summary = []
                has_unsupported = False
                
                for status, options in {'Not supported': [], 'Unknown': [], 'Accepted but ignored': [], 'Supported': []}.items():
                    for option, opt_status in data['options'].items():
                        if opt_status == status:
                            options.append(option)
                            if status == 'Not supported':
                                has_unsupported = True
                    if options:
                        options_summary.append(f"{status}: {', '.join(options)}")
                
                # If no unsupported options, set options_summary to ['None']
                if not has_unsupported and not options_summary:
                    options_summary = ['None']
                    
                # Create unknown options string
                unknown_options_str = ', '.join(unknown_options) if unknown_options else 'None'
                
                # Only include jobs with non-supported options or if all jobs have fewer than 20 entries
                if risk_level != 'None' or len(self.analysis_results['job_references']) < 20:
                    job_rows.append([
                        job_ref,
                        data['statement_type'],
                        risk_level,
                        status_counts['Supported'],
                        status_counts['Not supported'],
                        status_counts['Accepted but ignored'],
                        status_counts['Unknown'],
                        '\n'.join(options_summary),
                        unknown_options_str
                    ])
                
            df_jobs = pd.DataFrame(job_rows, columns=[
                'Job Reference', 
                'Statement Type', 
                'Risk Level',
                'Supported Options Count', 
                'Not Supported Options Count', 
                'Accepted but Ignored Count', 
                'Unknown Options Count', 
                'Options Details',
                'Unknown Options'
            ])
            df_jobs.to_excel(writer, sheet_name='Job References', index=False)
            
            # Format Job References sheet
            worksheet = writer.sheets['Job References']
            for col_num, value in enumerate(df_jobs.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Write data without color coding
            for row_num, (_, row) in enumerate(df_jobs.iterrows(), start=1):
                for col_num in range(len(df_jobs.columns)):
                    worksheet.write(row_num, col_num, row[df_jobs.columns[col_num]], wrap_format)
            
            # Adjust column widths to match jcl_utilscan style
            column_widths = [30, 20, 15, 15, 15, 15, 15, 50]  # Widths for each column
            for i, width in enumerate(column_widths):
                worksheet.set_column(i, i, width)
                
            # Set row heights for better readability of options details - ensure all content is visible without excess space
            for row_num in range(1, len(df_jobs) + 1):
                # Calculate appropriate row height based on content
                max_text_lines = 1
                for col_idx, col_name in enumerate(df_jobs.columns):
                    try:
                        if pd.notna(df_jobs.iloc[row_num-1, col_idx]):
                            text = str(df_jobs.iloc[row_num-1, col_idx])
                            # For Options Details column, count actual lines with minimal padding
                            if col_name == 'Options Details':
                                lines = len(text.split('\n'))
                                # Add minimal padding for Options Details to ensure visibility without excess space
                                max_text_lines = max(max_text_lines, lines + 1)  # Reduced padding from +2 to +1
                            elif col_name == 'Unknown Options':
                                # Handle Unknown Options column similarly
                                lines = len(text.split('\n'))
                                max_text_lines = max(max_text_lines, lines + 1)
                            else:  # For other columns, estimate based on text length and column width
                                # Use a default column width if index is out of range
                                col_width = column_widths[min(col_idx, len(column_widths)-1)]
                                estimated_lines = max(1, len(text) // (col_width * 2) + text.count('\n') + 1)
                                max_text_lines = max(max_text_lines, estimated_lines)
                    except Exception as e:
                        logger.error(f"Error processing cell at row {row_num}, col {col_idx} ({col_name}): {str(e)}")
                
                # Set row height with more precise calculation (16 points per line)
                # Reduced from 18 to 16 points per line for more compact display
                row_height = max(20, max_text_lines * 16)  # Reduced minimum from 25 to 20
                worksheet.set_row(row_num, row_height)
            
            # Save the Excel file
            writer.close()
            logger.info(f"Excel report generated: {output_file} (version {version})")
            print(f"Analysis complete. Report saved to: {output_file} (version {version})")
            return output_file
        except Exception as e:
            logger.error(f"Error generating Excel report: {str(e)}")
            return False
        
    def _get_next_version_number(self):
        """Determine the next version number based on existing files"""
        output_dir = Path(self.output_dir)
        existing_files = glob.glob(str(output_dir / "adrdssu_impact_analysis_v*.xlsx"))
        
        if not existing_files:
            return 1
            
        versions = []
        for file in existing_files:
            match = re.search(r'adrdssu_impact_analysis_v(\d+)\.xlsx$', file)
            if match:
                versions.append(int(match.group(1)))
                
        if versions:
            return max(versions) + 1
        else:
            return 1
    
    def run_analysis(self):
        """Run the complete analysis process"""
        if not self.load_metadata():
            return False
            
        if not self.load_excel_report():
            return False
            
        if not self.analyze_data():
            return False
            
        return self.generate_excel_report()


def main():
    """Main function to run the ADRDSSU impact analyzer"""
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)  # Parent directory of modules
    
    # Define paths
    yaml_path = os.path.join(base_dir, 'adrdssu_metadata.yaml')
    
    # Look for the latest JCL utilities report in the output directory
    output_dir = os.path.join(base_dir, 'output', 'jcl_utilities')
    if not os.path.exists(output_dir):
        logger.error(f"Output directory not found: {output_dir}")
        return False
        
    # Find the latest Excel report
    excel_files = [f for f in os.listdir(output_dir) if f.startswith('jcl_utilities_report_default') and f.endswith('.xlsx')]
    if not excel_files:
        logger.error(f"No JCL utilities report found in {output_dir}")
        return False
        
    # Sort by version number (assuming format is jcl_utilities_report_default_v{N}.xlsx)
    excel_files.sort(key=lambda f: int(re.search(r'_v(\d+)\.xlsx$', f).group(1)) if re.search(r'_v(\d+)\.xlsx$', f) else 0, reverse=True)
    latest_excel = os.path.join(output_dir, excel_files[0])
    
    # Define output directory
    analysis_output_dir = os.path.join(base_dir, 'output', 'impact_analysis')
    
    # Run the analyzer
    analyzer = ADRDSSUImpactAnalyzer(yaml_path, latest_excel, analysis_output_dir)
    result = analyzer.run_analysis()
    
    if result:
        print(f"Analysis complete. Report saved to: {result}")
        return True
    else:
        print("Analysis failed. Check the logs for details.")
        return False


if __name__ == "__main__":
    main()
