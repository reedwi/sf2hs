import click

from sf2hs.core.salesforce import SalesforceClient
from sf2hs.cli.utils.display import display_error, display_warning, display_success
from sf2hs.config.loader import load_config, get_default_config
from sf2hs.utils.file_handlers import save_to_excel, save_to_json
from sf2hs.utils.validators import filter_fields

@click.command()
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
        config_data = load_config(config) if config else get_default_config()

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
                display_warning(f"Object '{obj_name}' does not exist in Salesforce")
                continue

            fields = sf_client.get_object_fields(obj_name)
            
            # Filter fields if needed
            if not show_all:
                fields = [f for f in fields if f['can_migrate']]
                
            # Apply field filtering from config if available
            if config and 'objects' in config_data:
                obj_config = next(
                    (obj for obj in config_data['objects'] if obj['name'] == obj_name),
                    {}
                )
                fields = filter_fields(fields, obj_config)
                
            fields_data[obj_name] = fields

        # Save to file
        if format == 'excel':
            save_to_excel(fields_data, output)
        else:
            save_to_json(fields_data, output)

        display_success(f"Successfully saved fields to {output}")

    except Exception as e:
        display_error(f"Error saving fields: {str(e)}") 