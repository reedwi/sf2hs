from typing import Dict, List

def validate_field_data(fields_data: Dict[str, List[Dict]]) -> List[str]:
    """Validate the structure and content of loaded field data.
    
    Args:
        fields_data: Dictionary mapping object names to their field lists
        
    Returns:
        List of validation error messages, empty if valid
    """
    errors = []
    required_fields = {
        'name', 'label', 'type', 'required', 'unique', 
        'updateable', 'can_migrate', 'migration_type'
    }
    
    for object_name, fields in fields_data.items():
        if not fields:
            errors.append(f"No fields found for object '{object_name}'")
            continue
            
        for i, field in enumerate(fields):
            # Check required fields
            missing_fields = required_fields - set(field.keys())
            if missing_fields:
                errors.append(
                    f"Object '{object_name}', field {i+1}: "
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Validate field types
            if not isinstance(field['name'], str):
                errors.append(
                    f"Object '{object_name}', field {i+1}: "
                    "Field name must be a string"
                )
            
            if not isinstance(field['can_migrate'], bool):
                errors.append(
                    f"Object '{object_name}', field {i+1}: "
                    "can_migrate must be a boolean"
                )
            
            # Validate picklist values if present
            if field['type'] == 'picklist' and field.get('picklist_values'):
                if not isinstance(field['picklist_values'], list):
                    errors.append(
                        f"Object '{object_name}', field {i+1}: "
                        "picklist_values must be a list"
                    )
                else:
                    for j, value in enumerate(field['picklist_values']):
                        if not isinstance(value, dict) or 'label' not in value or 'value' not in value:
                            errors.append(
                                f"Object '{object_name}', field {i+1}, "
                                f"picklist value {j+1}: Must have 'label' and 'value' keys"
                            )
    
    return errors

def filter_fields(fields: List[Dict], object_config: Dict) -> List[Dict]:
    """Filter fields based on object configuration and apply HubSpot property mapping.
    
    Args:
        fields: List of field metadata dictionaries
        object_config: Object configuration from config file
        
    Returns:
        Filtered list of fields with HubSpot property names
    """
    if not object_config.get('fields'):
        return fields
        
    # Create a map of Salesforce field names to their config
    field_configs = {
        f['name']: f.get('hubspot_property')
        for f in object_config['fields']
    }
    
    filtered_fields = []
    for field in fields:
        field_name = field['name']
        
        # Only include fields that are explicitly listed
        if field_name not in field_configs:
            continue
            
        # Add HubSpot property name if specified
        hubspot_property = field_configs[field_name]
        if hubspot_property:
            field['hubspot_property'] = hubspot_property
            
        filtered_fields.append(field)
        
    return filtered_fields 