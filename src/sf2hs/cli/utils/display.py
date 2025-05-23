from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.style import Style
from typing import Dict

console = Console()

def display_error(message: str, title: str = "Error") -> None:
    """Display an error message in a panel.
    
    Args:
        message: The error message to display
        title: The panel title
    """
    console.print(Panel.fit(
        message,
        title=title,
        border_style="red"
    ))

def display_success(message: str, title: str = "Success") -> None:
    """Display a success message in a panel.
    
    Args:
        message: The success message to display
        title: The panel title
    """
    console.print(Panel.fit(
        message,
        title=title,
        border_style="green"
    ))

def display_warning(message: str, title: str = "Warning") -> None:
    """Display a warning message in a panel.
    
    Args:
        message: The warning message to display
        title: The panel title
    """
    console.print(Panel.fit(
        message,
        title=title,
        border_style="yellow"
    ))

def display_info(message: str, title: str = "Info") -> None:
    """Display an info message in a panel.
    
    Args:
        message: The info message to display
        title: The panel title
    """
    console.print(Panel.fit(
        message,
        title=title,
        border_style="blue"
    ))

def create_fields_table(object_name: str) -> Table:
    """Create a table for displaying field information.
    
    Args:
        object_name: Name of the Salesforce object
        
    Returns:
        Rich Table object configured for field display
    """
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
        title=f"Fields for {object_name}",
        box=box.ROUNDED
    )
    return table

def get_field_row_style(field: Dict) -> Style:
    """Get the style for a field row based on its properties.
    
    Args:
        field: Field data dictionary
        
    Returns:
        Rich Style object for the row
    """
    if not field['can_migrate']:
        return Style(color="red", dim=True)
    elif field['migration_type'] == 'user_reference':
        return Style(color="blue")
    else:
        return Style(color="green")

def display_field_legend() -> None:
    """Display the legend for field table colors."""
    console.print("\n[bold]Legend:[/bold]")
    console.print("[green]Green[/green] - Field can be migrated")
    console.print("[blue]Blue[/blue] - User reference field (will be mapped to HubSpot user field)")
    console.print("[red dim]Red (dimmed)[/red dim] - Field cannot be migrated\n") 