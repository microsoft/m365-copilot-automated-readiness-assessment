"""  
Permission checking utilities to detect admin roles and provide helpful guidance.
"""
import asyncio


async def check_admin_permissions(client, tenant_id, services=None):
    """
    Basic connectivity test for Service Principal authentication.
    
    Args:
        client: Graph client
        tenant_id: Azure tenant ID (GUID or domain name)
        services: List of services (ignored for SP - permissions are pre-configured)
    
    Returns:
        dict with basic connection status
    """
    result = {
        'connected': False,
        'tenant_name': None,
        'tenant_id': tenant_id,
        'auth_type': 'Service Principal',
        'warnings': []
    }
    
    try:
        # Simple connectivity test - get organization info
        org = await client.organization.get()
        if org and org.value and len(org.value) > 0:
            result['connected'] = True
            result['tenant_name'] = org.value[0].display_name
            result['tenant_id'] = org.value[0].id
    except Exception as e:
        result['warnings'].append(f"Connection test failed: {str(e)}")
    
    return result


def print_permission_status(permission_check, services=None):
    """Print simplified connection status for Service Principal"""
    print("\n" + "="*80)
    print("CONNECTION STATUS")
    print("="*80)
    
    if permission_check.get('connected'):
        print(f"✅ Connected to Microsoft Graph")
        if permission_check.get('tenant_name'):
            print(f"   Tenant: {permission_check['tenant_name']}")
        print(f"   Auth: {permission_check.get('auth_type', 'Service Principal')}")
    else:
        print(f"❌ Connection failed")
    
    if permission_check.get('warnings'):
        print(f"\n⚠️  Warnings:")
        for warning in permission_check['warnings']:
            print(f"  • {warning}")
    
    print("="*80 + "\n")
