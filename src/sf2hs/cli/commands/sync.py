import click
from sf2hs.cli.utils.display import display_error, display_warning, display_info
from sf2hs.config.loader import load_config, get_default_config
from sf2hs.core.salesforce import SalesforceClient
from sf2hs.utils.file_handlers import load_from_excel, load_from_json
from sf2hs.utils.validators import validate_field_data, filter_fields

@click.command()
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
@click.option(
    '--fields-file', '-f',
    type=click.Path(exists=True),
    help='Path to Excel or JSON file containing field data (optional)'
)
@click.option(
    '--format', '-fmt',
    type=click.Choice(['excel', 'json']),
    default='excel',
    help='Format of the fields file (default: excel)'
)
@click.option(
    '--direct/--transformed',
    default=False,
    help='Direct sync from Salesforce (no transformation) or use transformed data'
)
def sync(config, object, env_file, fields_file, format, direct):
    """Synchronize Salesforce fields to HubSpot properties.
    
    This command supports three modes:
    1. Config-based sync: Use configuration file to determine objects and fields
    2. Direct sync: Synchronize fields directly from Salesforce to HubSpot
    3. Transformed sync: Use pre-transformed field data from a file
    
    Examples:
        # Config-based sync
        sf2hs sync --config config/my_config.yaml
        
        # Direct sync from Salesforce
        sf2hs sync --object Account --direct
        
        # Sync using transformed data
        sf2hs sync --fields-file fields.xlsx --transformed
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

        fields_data = {}
        
        if config and 'objects' in config_data:
            # Config-based sync mode
            for obj_config in config_data['objects']:
                obj_name = obj_config['name']
                
                if not sf_client.validate_object_exists(obj_name):
                    display_warning(f"Object '{obj_name}' does not exist in Salesforce")
                    continue
                    
                fields = sf_client.get_object_fields(obj_name)
                fields = filter_fields(fields, obj_config)
                fields_data[obj_name] = fields
                
        elif direct:
            # Direct sync mode
            if not object:
                display_error("Please specify a Salesforce object using --object for direct sync")
                return

            if not sf_client.validate_object_exists(object):
                display_error(f"Object '{object}' does not exist in Salesforce")
                return

            fields = sf_client.get_object_fields(object)
            fields_data = {object: fields}
            
        else:
            # Transformed sync mode
            if not fields_file:
                display_error("Please specify a fields file using --fields-file for transformed sync")
                return

            # Load and validate fields data
            if format == 'excel':
                fields_data = load_from_excel(fields_file)
            else:
                fields_data = load_from_json(fields_file)

            errors = validate_field_data(fields_data)
            if errors:
                display_error(
                    "Validation errors found:\n" + "\n".join(f"- {e}" for e in errors)
                )
                return

        # TODO: Implement actual sync logic with HubSpot
        display_info(
            f"Starting sync process...\n"
            f"Mode: {'Config-based' if config and 'objects' in config_data else 'Direct' if direct else 'Transformed'}\n"
            f"Objects: {', '.join(fields_data.keys())}"
        )

    except Exception as e:
        display_error(f"Error during sync: {str(e)}") 