import json
from typing import Dict, List

import pandas as pd

def save_to_excel(fields_data: Dict[str, List[Dict]], output_path: str) -> None:
    """Save fields data to Excel file with multiple sheets.
    
    Args:
        fields_data: Dictionary mapping object names to their field lists
        output_path: Path to save the Excel file
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for object_name, fields in fields_data.items():
            df = pd.DataFrame(fields)
            
            # Convert migration_notes list to string
            if 'migration_notes' in df.columns:
                df['migration_notes'] = df['migration_notes'].apply(lambda x: '\n'.join(x) if x else '')
            
            df.to_excel(writer, sheet_name=object_name, index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets[object_name]
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

def save_to_json(fields_data: Dict[str, List[Dict]], output_path: str) -> None:
    """Save fields data to JSON file.
    
    Args:
        fields_data: Dictionary mapping object names to their field lists
        output_path: Path to save the JSON file
    """
    with open(output_path, 'w') as f:
        json.dump(fields_data, f, indent=2)

def load_from_excel(input_path: str) -> Dict[str, List[Dict]]:
    """Load fields data from Excel file with multiple sheets.
    
    Args:
        input_path: Path to the Excel file
        
    Returns:
        Dictionary mapping object names to their field lists
    """
    fields_data = {}
    excel_file = pd.ExcelFile(input_path)
    
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Convert migration_notes string back to list
        if 'migration_notes' in df.columns:
            df['migration_notes'] = df['migration_notes'].apply(
                lambda x: x.split('\n') if pd.notna(x) and x else []
            )
            
        # Convert picklist_values string back to list of dicts if present
        if 'picklist_values' in df.columns:
            df['picklist_values'] = df['picklist_values'].apply(
                lambda x: json.loads(x) if pd.notna(x) and x else None
            )
            
        fields_data[sheet_name] = df.to_dict('records')
        
    return fields_data

def load_from_json(input_path: str) -> Dict[str, List[Dict]]:
    """Load fields data from JSON file.
    
    Args:
        input_path: Path to the JSON file
        
    Returns:
        Dictionary mapping object names to their field lists
    """
    with open(input_path, 'r') as f:
        return json.load(f) 