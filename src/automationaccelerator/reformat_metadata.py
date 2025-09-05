#!/usr/bin/env python3
"""
Script to reformat utilities_metadata.yaml to match the structure of adrdssu_metadata.yaml
"""
import yaml
from pathlib import Path

def reformat_metadata():
    """
    Reformat utilities_metadata.yaml to match the structure of adrdssu_metadata.yaml
    """
    # Load the utilities metadata YAML file
    with open('utilities_metadata.yaml', 'r') as f:
        utilities_metadata = yaml.safe_load(f)

    # Create a new dictionary with the desired structure
    reformatted_metadata = {}

    # Process each utility
    for utility, utility_data in utilities_metadata.items():
        # Skip if utility_data is None
        if utility_data is None:
            print(f"Warning: No data for utility '{utility}'. Skipping.")
            reformatted_metadata[utility] = {"Statements": {}}
            continue
            
        reformatted_metadata[utility] = {"Statements": {}}
        
        # Process each statement
        for statement, statement_data in utility_data.get("Supported Statements", {}).items():
            reformatted_metadata[utility]["Statements"][statement] = {
                "Supported": [],
                "Not supported": [],
                "Accepted but ignored": []
            }
            
            # Process each option/clause
            for option, status in statement_data.get("Options/Clauses", {}).items():
                # Handle different types of status values
                if isinstance(status, str):
                    # Extract the base status (ignore any explanatory text)
                    base_status = status.split('(')[0].strip() if '(' in status else status.strip()
                    
                    # Map the status to one of the three categories
                    if base_status.lower() == "supported" or base_status.lower() == "required":
                        reformatted_metadata[utility]["Statements"][statement]["Supported"].append(option)
                    elif base_status.lower() == "not supported":
                        reformatted_metadata[utility]["Statements"][statement]["Not supported"].append(option)
                    elif base_status.lower() == "accepted but ignored":
                        reformatted_metadata[utility]["Statements"][statement]["Accepted but ignored"].append(option)
                    elif "partially supported" in base_status.lower():
                        # Add partially supported to the Supported category
                        reformatted_metadata[utility]["Statements"][statement]["Supported"].append(option)
                        print(f"Note: Mapped 'Partially supported' to 'Supported' for option '{option}' in statement '{statement}' of utility '{utility}'")
                    else:
                        print(f"Warning: Unknown status '{status}' for option '{option}' in statement '{statement}' of utility '{utility}'")
                        # Default to Not supported for unknown status
                        reformatted_metadata[utility]["Statements"][statement]["Not supported"].append(option)
                elif isinstance(status, dict) or status is None:
                    # For complex or empty values, default to Not supported
                    reformatted_metadata[utility]["Statements"][statement]["Not supported"].append(option)
                    print(f"Warning: Complex or empty status for option '{option}' in statement '{statement}' of utility '{utility}'. Defaulting to 'Not supported'.")
                else:
                    print(f"Warning: Unexpected status type {type(status)} for option '{option}' in statement '{statement}' of utility '{utility}'")
                    # Default to Not supported for unexpected types
                    reformatted_metadata[utility]["Statements"][statement]["Not supported"].append(option)
    
    # Sort the options alphabetically within each category
    for utility, utility_data in reformatted_metadata.items():
        for statement, statement_data in utility_data["Statements"].items():
            for status, options in statement_data.items():
                statement_data[status] = sorted(options)
    
    # Write the reformatted metadata to a new YAML file
    with open('utilities_metadata_reformatted.yaml', 'w') as f:
        yaml.dump(reformatted_metadata, f, default_flow_style=False, sort_keys=False)

    print("Reformatting complete. Output saved to utilities_metadata_reformatted.yaml")

if __name__ == "__main__":
    reformat_metadata()
