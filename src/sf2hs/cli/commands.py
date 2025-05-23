import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.style import Style
from ..core.salesforce import SalesforceClient
import yaml
from pathlib import Path
import pandas as pd
import json
from typing import List, Dict, Optional

console = Console()

def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(Panel.fit(
            f"Failed to load configuration: {str(e)}",
            title="Configuration Error",
            border_style="red"
        ))
        raise

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

@click.group()
def cli():
    """Salesforce to HubSpot metadata synchronization tool.
    
    This tool helps you synchronize Salesforce metadata (fields, objects, etc.)
    to HubSpot properties. It supports both configuration-based and direct
    command-line operations.
    
    Example:
        sf2hs list-fields --object Account --config config/my_config.yaml
    """
    pass

@cli.command()
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Path to YAML configuration file containing sync settings and mappings'
)
@click.option(
    '--object', '-o',
    help='Salesforce object to synchronize (e.g., Account, Contact, Lead)'
)
@click.option(
    '--env-file', '-e',
    type=click.Path(exists=True),
    default='.env',
    help='Path to .env file containing credentials (default: .env in current directory)'
)
def sync(config, object, env_file):
    """Synchronize Salesforce fields to HubSpot properties.
    
    This command will:
    1. Read the configuration file
    2. Connect to Salesforce and HubSpot
    3. Map Salesforce fields to HubSpot properties
    4. Create or update properties in HubSpot
    
    Example:
        sf2hs sync --config config/my_config.yaml --object Account
    """
    console.print(Panel.fit(
        f"Starting sync process...\nConfig: {config}\nObject: {object}",
        title="Sync Operation",
        border_style="blue"
    ))

@cli.command()
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Path to YAML configuration file to validate'
)
@click.option(
    '--env-file', '-e',
    type=click.Path(exists=True),
    default='.env',
    help='Path to .env file containing credentials (default: .env in current directory)'
)
def validate(config, env_file):
    """Validate the configuration file.
    
    This command will:
    1. Check the configuration file syntax
    2. Validate Salesforce credentials
    3. Verify object and field mappings
    4. Check HubSpot API access
    
    Example:
        sf2hs validate --config config/my_config.yaml
    """
    console.print(Panel.fit(
        f"Validating configuration file: {config}",
        title="Validation",
        border_style="green"
    ))

@cli.command()
@click.option(
    '--object', '-o',
    help='Salesforce object to list fields for (e.g., Account, Contact, Lead)'
)
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Path to YAML configuration file (optional, uses default settings if not provided)'
)
@click.option(
    '--env-file', '-e',
    type=click.Path(exists=True),
    default='.env',
    help='Path to .env file containing credentials (default: .env in current directory)'
)
@click.option(
    '--show-all/--hide-non-migratable',
    default=True,
    help='Show all fields or only migratable fields'
)
def list_fields(object, config, env_file, show_all):
    """List available fields for a Salesforce object.
    
    This command will:
    1. Connect to Salesforce
    2. Retrieve all fields for the specified object
    3. Display field details including:
       - Field name
       - Label
       - Data type
       - Required status
       - Unique status
       - Updateable status
       - Migration status
       - Migration notes
    
    Example:
        sf2hs list-fields --object Account --config config/my_config.yaml
    """
    if not object:
        console.print(Panel.fit(
            "Please specify a Salesforce object using --object",
            title="Error",
            border_style="red"
        ))
        return

    try:
        # Load configuration
        config_data = load_config(config) if config else {
            'salesforce': {
                'instance_url': 'https://login.salesforce.com',
                'api_version': '57.0'
            }
        }

        # Initialize and authenticate Salesforce client
        sf_client = SalesforceClient(
            instance_url=config_data['salesforce']['instance_url'],
            api_version=config_data['salesforce']['api_version'],
            env_file=env_file
        )
        sf_client.authenticate()

        # Validate object exists
        if not sf_client.validate_object_exists(object):
            console.print(Panel.fit(
                f"Object '{object}' does not exist in Salesforce",
                title="Error",
                border_style="red"
            ))
            return

        # Get fields
        fields = sf_client.get_object_fields(object)

        # Filter fields if needed
        if not show_all:
            fields = [f for f in fields if f['can_migrate']]

        # Create and display table
        table = Table(
            "Field Name",
            "Label",
            "Type",
            "Required",
            "Unique",
            "Updateable",
            "Can Migrate",
            "Migration Type",
            "Notes",
            title=f"Fields for {object}",
            box=box.ROUNDED
        )

        # Define styles
        non_migratable_style = Style(color="red", dim=True)
        migratable_style = Style(color="green")
        user_reference_style = Style(color="blue")

        for field in fields:
            # Determine row style based on migration status and type
            if not field['can_migrate']:
                row_style = non_migratable_style
            elif field['migration_type'] == 'user_reference':
                row_style = user_reference_style
            else:
                row_style = migratable_style
            
            table.add_row(
                field['name'],
                field['label'],
                field['type'],
                str(field['required']),
                str(field['unique']),
                str(field['updateable']),
                str(field['can_migrate']),
                field['migration_type'],
                '\n'.join(field['migration_notes']) if field['migration_notes'] else '',
                style=row_style
            )

        # Add a legend
        console.print("\n[bold]Legend:[/bold]")
        console.print("[green]Green[/green] - Field can be migrated")
        console.print("[blue]Blue[/blue] - User reference field (will be mapped to HubSpot user field)")
        console.print("[red dim]Red (dimmed)[/red dim] - Field cannot be migrated\n")

        console.print(table)

    except Exception as e:
        console.print(Panel.fit(
            f"Error listing fields: {str(e)}",
            title="Error",
            border_style="red"
        ))

@cli.command()
@click.option(
    '--config', '-c',
    type=click.Path(exists=True),
    help='Path to YAML configuration file containing object mappings'
)
@click.option(
    '--object', '-o',
    help='Salesforce object to save fields for (e.g., Account, Contact, Lead)'
)
@click.option(
    '--output', '-out',
    type=click.Path(),
    default='salesforce_fields.xlsx',
    help='Output file path (default: salesforce_fields.xlsx)'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['excel', 'json']),
    default='excel',
    help='Output format (default: excel)'
)
@click.option(
    '--env-file', '-e',
    type=click.Path(exists=True),
    default='.env',
    help='Path to .env file containing credentials (default: .env in current directory)'
)
@click.option(
    '--show-all/--hide-non-migratable',
    default=True,
    help='Include all fields or only migratable fields'
)
def save_fields(config, object, output, format, env_file, show_all):
    """Save Salesforce fields to Excel or JSON file.
    
    This command will:
    1. Read objects from config file or use specified object
    2. Connect to Salesforce
    3. Retrieve all fields for each object
    4. Save to Excel (with multiple sheets) or JSON file
    
    Example:
        # Save fields for objects in config file
        sf2hs save-fields --config config/my_config.yaml
        
        # Save fields for specific object
        sf2hs save-fields --object Account
        
        # Save as JSON
        sf2hs save-fields --object Account --format json --output fields.json
    """
    try:
        # Load configuration
        config_data = load_config(config) if config else {
            'salesforce': {
                'instance_url': 'https://login.salesforce.com',
                'api_version': '57.0'
            }
        }

        # Initialize and authenticate Salesforce client
        sf_client = SalesforceClient(
            instance_url=config_data['salesforce']['instance_url'],
            api_version=config_data['salesforce']['api_version'],
            env_file=env_file
        )
        sf_client.authenticate()

        # Determine objects to process
        objects_to_process = []
        if object:
            objects_to_process = [object]
        elif config and 'objects' in config_data:
            objects_to_process = [obj['name'] for obj in config_data['objects']]
        else:
            raise ValueError("Please specify either --object or provide a config file with objects")

        # Get fields for each object
        fields_data = {}
        for obj_name in objects_to_process:
            if not sf_client.validate_object_exists(obj_name):
                console.print(Panel.fit(
                    f"Warning: Object '{obj_name}' does not exist in Salesforce",
                    title="Warning",
                    border_style="yellow"
                ))
                continue

            fields = sf_client.get_object_fields(obj_name)
            
            # Filter fields if needed
            if not show_all:
                fields = [f for f in fields if f['can_migrate']]
                
            fields_data[obj_name] = fields

        # Save to file
        if format == 'excel':
            save_to_excel(fields_data, output)
        else:
            save_to_json(fields_data, output)

        console.print(Panel.fit(
            f"Successfully saved fields to {output}",
            title="Success",
            border_style="green"
        ))

    except Exception as e:
        console.print(Panel.fit(
            f"Error saving fields: {str(e)}",
            title="Error",
            border_style="red"
        ))

if __name__ == '__main__':
    cli() 