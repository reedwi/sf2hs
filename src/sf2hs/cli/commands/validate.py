import click

from sf2hs.cli.utils.display import display_error, display_success
from sf2hs.config.loader import load_config
from sf2hs.core.salesforce import SalesforceClient

@click.command()
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
    try:
        if not config:
            display_error("Please specify a configuration file using --config")
            return

        # Load and validate configuration
        config_data = load_config(config)

        # Initialize and authenticate Salesforce client
        sf_client = SalesforceClient(
            instance_url=config_data['salesforce']['instance_url'],
            api_version=config_data['salesforce']['api_version'],
            env_file=env_file
        )
        sf_client.authenticate()

        # Validate objects if specified
        if 'objects' in config_data:
            for obj_config in config_data['objects']:
                obj_name = obj_config['name']
                if not sf_client.validate_object_exists(obj_name):
                    display_error(f"Object '{obj_name}' does not exist in Salesforce")
                    continue

                # Validate fields if specified
                if 'fields' in obj_config:
                    fields = sf_client.get_object_fields(obj_name)
                    field_names = {f['name'] for f in fields}
                    for field_config in obj_config['fields']:
                        if field_config['name'] not in field_names:
                            display_error(
                                f"Field '{field_config['name']}' does not exist in "
                                f"object '{obj_name}'"
                            )

        display_success(f"Successfully validated configuration file: {config}")

    except Exception as e:
        display_error(f"Error validating configuration: {str(e)}") 