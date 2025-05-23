import os
from pathlib import Path
from typing import Dict, List, Optional
from simple_salesforce import Salesforce
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

console = Console()

class SalesforceClient:
    """Client for interacting with Salesforce API."""
    
    def __init__(self, instance_url: str, api_version: str, env_file: Optional[str] = None):
        """Initialize the Salesforce client.
        
        Args:
            instance_url: Salesforce instance URL
            api_version: Salesforce API version
            env_file: Optional path to .env file for credentials
        """
        self.instance_url = instance_url
        self.api_version = api_version
        self._client = None
        
        # Load environment variables from .env file if provided
        if env_file:
            env_path = Path(env_file)
            if env_path.exists():
                load_dotenv(env_path)
                console.print(Panel.fit(
                    f"Loaded environment variables from {env_file}",
                    title="Environment",
                    border_style="blue"
                ))
            else:
                console.print(Panel.fit(
                    f"Warning: .env file not found at {env_file}",
                    title="Environment",
                    border_style="yellow"
                ))
        
    def _get_credentials(self) -> Dict[str, str]:
        """Get Salesforce credentials from environment variables.
        
        Returns:
            Dictionary containing username, password, and security token
            
        Raises:
            ValueError: If required credentials are missing
        """
        credentials = {
            'username': os.getenv('SF_USERNAME'),
            'password': os.getenv('SF_PASSWORD'),
            'security_token': os.getenv('SF_SECURITY_TOKEN')
        }
        
        # Check for missing credentials
        missing = [k for k, v in credentials.items() if not v]
        if missing:
            raise ValueError(
                f"Missing required Salesforce credentials: {', '.join(missing)}. "
                "Please set them in your environment or .env file:\n"
                "SF_USERNAME=your_username\n"
                "SF_PASSWORD=your_password\n"
                "SF_SECURITY_TOKEN=your_security_token"
            )
            
        return credentials
        
    def authenticate(self) -> None:
        """Authenticate with Salesforce using environment variables."""
        try:
            credentials = self._get_credentials()
            
            self._client = Salesforce(
                username=credentials['username'],
                password=credentials['password'],
                security_token=credentials['security_token'],
                instance_url=self.instance_url,
                version=self.api_version
            )
            
            console.print(Panel.fit(
                "Successfully authenticated with Salesforce",
                title="Authentication",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(Panel.fit(
                f"Failed to authenticate with Salesforce: {str(e)}",
                title="Authentication Error",
                border_style="red"
            ))
            raise

    def _is_system_field(self, field: Dict) -> bool:
        """Check if a field is a system field that shouldn't be migrated.
        
        Args:
            field: Field metadata dictionary
            
        Returns:
            True if the field is a system field that shouldn't be migrated
        """
        system_fields = {
            'CreatedById', 'LastModifiedById', 'CreatedDate', 'LastModifiedDate',
            'SystemModstamp', 'LastViewedDate', 'LastReferencedDate'
        }
        return field['name'] in system_fields

    def _is_formula_field(self, field: Dict) -> bool:
        """Check if a field is a formula field.
        
        Args:
            field: Field metadata dictionary
            
        Returns:
            True if the field is a formula field
        """
        return field.get('calculated', False)

    def _is_reference_field(self, field: Dict) -> bool:
        """Check if a field is a reference field.
        
        Args:
            field: Field metadata dictionary
            
        Returns:
            True if the field is a reference field
        """
        return field['type'] == 'reference'

    def _is_user_reference(self, field: Dict) -> bool:
        """Check if a reference field points to a User object.
        
        Args:
            field: Field metadata dictionary
            
        Returns:
            True if the field is a reference to a User object
        """
        if not self._is_reference_field(field):
            return False
            
        # Check if the reference is to a User object
        return field.get('referenceTo', []) == ['User']

    def _is_address_field(self, field: Dict) -> bool:
        """Check if a field is an address field.
        
        Args:
            field: Field metadata dictionary
            
        Returns:
            True if the field is an address field
        """
        return field['type'] == 'address'

    def _get_migration_status(self, field: Dict) -> Dict:
        """Get migration status and notes for a field.
        
        Args:
            field: Field metadata dictionary
            
        Returns:
            Dictionary containing migration status and notes
        """
        status = {
            'can_migrate': True,
            'migration_type': 'direct',
            'notes': []
        }

        # Check for system fields
        if self._is_system_field(field):
            status['can_migrate'] = False
            status['notes'].append('System field - exists in HubSpot')
            return status

        # Check for formula fields
        if self._is_formula_field(field):
            status['can_migrate'] = False
            status['notes'].append('Formula field - requires custom implementation')
            return status

        # Check for reference fields
        if self._is_reference_field(field):
            if self._is_user_reference(field):
                status['migration_type'] = 'user_reference'
                status['notes'].append('User reference field - will be mapped to HubSpot user field')
            else:
                status['migration_type'] = 'association'
                status['notes'].append('Reference field - usually created as association')
            return status

        # Check for address fields
        if self._is_address_field(field):
            status['can_migrate'] = False
            status['notes'].append('Address field - compound field type')
            return status

        return status
    
    def get_object_fields(self, object_name: str) -> List[Dict]:
        """Get all fields for a Salesforce object.
        
        Args:
            object_name: Name of the Salesforce object
            
        Returns:
            List of field metadata dictionaries
        """
        if not self._client:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
            
        try:
            # Get object description which includes field metadata
            object_desc = self._client.__getattr__(object_name).describe()
            
            fields = []
            for field in object_desc['fields']:
                # Get migration status
                migration_status = self._get_migration_status(field)
                
                field_info = {
                    'name': field['name'],
                    'label': field['label'],
                    'type': field['type'],
                    'length': field.get('length'),
                    'precision': field.get('precision'),
                    'scale': field.get('scale'),
                    'required': field['nillable'] is False,
                    'unique': field['unique'],
                    'updateable': field['updateable'],
                    'createable': field['createable'],
                    'picklist_values': [
                        {'label': v['label'], 'value': v['value']}
                        for v in field.get('picklistValues', [])
                    ] if field['type'] == 'picklist' else None,
                    'can_migrate': migration_status['can_migrate'],
                    'migration_type': migration_status['migration_type'],
                    'migration_notes': migration_status['notes']
                }
                fields.append(field_info)
            
            return fields
            
        except Exception as e:
            console.print(Panel.fit(
                f"Failed to get fields for object {object_name}: {str(e)}",
                title="Field Discovery Error",
                border_style="red"
            ))
            raise
    
    def get_object_metadata(self, object_name: str) -> Dict:
        """Get complete metadata for a Salesforce object.
        
        Args:
            object_name: Name of the Salesforce object
            
        Returns:
            Dictionary containing object metadata
        """
        if not self._client:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
            
        try:
            object_desc = self._client.__getattr__(object_name).describe()
            
            return {
                'name': object_desc['name'],
                'label': object_desc['label'],
                'label_plural': object_desc['labelPlural'],
                'key_prefix': object_desc['keyPrefix'],
                'createable': object_desc['createable'],
                'updateable': object_desc['updateable'],
                'deletable': object_desc['deletable'],
                'fields': self.get_object_fields(object_name)
            }
            
        except Exception as e:
            console.print(Panel.fit(
                f"Failed to get metadata for object {object_name}: {str(e)}",
                title="Metadata Error",
                border_style="red"
            ))
            raise
    
    def validate_object_exists(self, object_name: str) -> bool:
        """Validate that a Salesforce object exists.
        
        Args:
            object_name: Name of the Salesforce object
            
        Returns:
            True if object exists, False otherwise
        """
        if not self._client:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
            
        try:
            self._client.__getattr__(object_name).describe()
            return True
        except Exception:
            return False 