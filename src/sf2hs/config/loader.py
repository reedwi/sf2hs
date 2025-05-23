import yaml
from typing import Dict
from rich.console import Console
from rich.panel import Panel

console = Console()

def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Dictionary containing the configuration
        
    Raises:
        Exception: If configuration file cannot be loaded or parsed
    """
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

def get_default_config() -> Dict:
    """Get default configuration settings.
    
    Returns:
        Dictionary containing default configuration
    """
    return {
        'salesforce': {
            'instance_url': 'https://login.salesforce.com',
            'api_version': '57.0'
        }
    } 