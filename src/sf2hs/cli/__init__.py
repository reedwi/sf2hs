import click
from sf2hs.cli.commands.list import list_fields
from sf2hs.cli.commands.save import save_fields
from sf2hs.cli.commands.load import load_fields
from sf2hs.cli.commands.validate import validate
from sf2hs.cli.commands.sync import sync

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

# Register commands
cli.add_command(list_fields, name='list-fields')
cli.add_command(save_fields, name='save-fields')
cli.add_command(load_fields, name='load-fields')
cli.add_command(validate)
cli.add_command(sync)
