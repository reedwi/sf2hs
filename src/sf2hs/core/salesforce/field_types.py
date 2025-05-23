from typing import Dict

def is_system_field(field: Dict) -> bool:
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

def is_formula_field(field: Dict) -> bool:
    """Check if a field is a formula field.
    
    Args:
        field: Field metadata dictionary
        
    Returns:
        True if the field is a formula field
    """
    return field.get('calculated', False)

def is_reference_field(field: Dict) -> bool:
    """Check if a field is a reference field.
    
    Args:
        field: Field metadata dictionary
        
    Returns:
        True if the field is a reference field
    """
    return field['type'] == 'reference'

def is_user_reference(field: Dict) -> bool:
    """Check if a reference field points to a User object.
    
    Args:
        field: Field metadata dictionary
        
    Returns:
        True if the field is a reference to a User object
    """
    if not is_reference_field(field):
        return False
        
    # Check if the reference is to a User object
    return field.get('referenceTo', []) == ['User']

def is_address_field(field: Dict) -> bool:
    """Check if a field is an address field.
    
    Args:
        field: Field metadata dictionary
        
    Returns:
        True if the field is an address field
    """
    return field['type'] == 'address' 