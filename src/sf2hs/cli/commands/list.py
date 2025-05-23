import click

from sf2hs.core.salesforce import SalesforceClient
from sf2hs.cli.utils.display import (
    display_error, display_warning, create_fields_table,
    get_field_row_style, display_field_legend, console
)
from sf2hs.config.loader import load_config, get_default_config

@click.command()
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
        display_error("Please specify a Salesforce object using --object")
        return

    try:
        # Load configuration
        config_data = load_config(config) if config else get_default_config()

        # Initialize and authenticate Salesforce client
        sf_client = SalesforceClient(
            instance_url=config_data['salesforce']['instance_url'],
            api_version=config_data['salesforce']['api_version'],
            env_file=env_file
        )
        sf_client.authenticate()

        # Validate object exists
        if not sf_client.validate_object_exists(object):
            display_error(f"Object '{object}' does not exist in Salesforce")
            return

        # Get fields
        fields = sf_client.get_object_fields(object)

        # Filter fields if needed
        if not show_all:
            fields = [f for f in fields if f['can_migrate']]

        # Create and display table
        table = create_fields_table(object)

        for field in fields:
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
                style=get_field_row_style(field)
            )

        display_field_legend()
        console.print(table)

    except Exception as e:
        display_error(f"Error listing fields: {str(e)}") 