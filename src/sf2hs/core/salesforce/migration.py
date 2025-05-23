from typing import Dict

from sf2hs.core.salesforce.field_types import (
    is_system_field, is_formula_field, is_reference_field,
    is_user_reference, is_address_field
)

def get_migration_status(field: Dict) -> Dict:
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
    if is_system_field(field):
        status['can_migrate'] = False
        status['notes'].append('System field - exists in HubSpot')
        return status

    # Check for formula fields
    if is_formula_field(field):
        status['can_migrate'] = False
        status['notes'].append('Formula field - requires custom implementation')
        return status

    # Check for reference fields
    if is_reference_field(field):
        if is_user_reference(field):
            status['migration_type'] = 'user_reference'
            status['notes'].append('User reference field - will be mapped to HubSpot user field')
        else:
            status['migration_type'] = 'association'
            status['notes'].append('Reference field - usually created as association')
        return status

    # Check for address fields
    if is_address_field(field):
        status['can_migrate'] = False
        status['notes'].append('Address field - compound field type')
        return status

    return status 