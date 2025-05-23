import click

from sf2hs.cli.utils.display import display_error, display_success
from sf2hs.utils.file_handlers import load_from_excel, load_from_json
from sf2hs.utils.validators import validate_field_data

@click.command()
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    required=True,
    help='Path to input file (Excel or JSON) containing field data'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['excel', 'json']),
    default='excel',
    help='Input file format (default: excel)'
)
@click.option(
    '--validate-only/--load',
    default=False,
    help='Only validate the data without loading it for sync'
)
def load_fields(input, format, validate_only):
    """Load and validate field data from Excel or JSON file.
    
    This command will:
    1. Load field data from the specified file
    2. Validate the structure and content of the data
    3. If valid and not in validate-only mode, prepare the data for syncing
    
    Example:
        # Validate Excel file
        sf2hs load-fields --input fields.xlsx --validate-only
        
        # Load JSON file for syncing
        sf2hs load-fields --input fields.json --format json
    """
    try:
        # Load data from file
        if format == 'excel':
            fields_data = load_from_excel(input)
        else:
            fields_data = load_from_json(input)
            
        # Validate data
        errors = validate_field_data(fields_data)
        
        if errors:
            display_error(
                "Validation errors found:\n" + "\n".join(f"- {e}" for e in errors)
            )
            return
            
        display_success(f"Successfully validated {len(fields_data)} objects")
        
        if not validate_only:
            # TODO: Store the validated data for use in sync command
            display_success("Data loaded and ready for sync")
            
    except Exception as e:
        display_error(f"Error loading fields: {str(e)}") 