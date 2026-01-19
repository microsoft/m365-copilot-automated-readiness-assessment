import asyncio
from get_recommendation import get_recommendation
from service_categorization import determine_service_type
from spinner import get_timestamp, _stdout_lock
from azure.core.exceptions import HttpResponseError

async def fetch_entra_data(client):
    """Fetch raw Entra data from Graph API"""
    org, subscribed_skus, directory_roles = await asyncio.gather(
        client.organization.get(),
        client.subscribed_skus.get(),
        client.directory_roles.get()
    )
    return org, subscribed_skus, directory_roles

def process_entra_data(org, subscribed_skus, directory_roles):
    """Process Entra data into structured format"""
    org_details = org.value[0] if org.value else None
    
    entra_licenses = []
    
    for sku in subscribed_skus.value:
        # Get Entra/Azure AD related service plans from this SKU
        entra_plans = []
        if sku.service_plans:
            for plan in sku.service_plans:
                plan_name = plan.service_plan_name or ''
                # Check if this service plan is Entra/Azure AD related
                if any(keyword in plan_name.upper() for keyword in ['AAD_', 'ENTRA', 'MFA', 'IDENTITY_PROTECTION', 'CONDITIONAL_ACCESS', 'GOVERNANCE', 'PRIVILEGED_IDENTITY', 'PREMIUM_P1', 'PREMIUM_P2', 'INTUNE']):
                    entra_plans.append({
                        'name': plan_name,
                        'status': plan.provisioning_status or 'Unknown'
                    })
        
        # Include SKU if it has Entra plans or is an Entra-specific license
        sku_name = sku.sku_part_number or ''
        if entra_plans or any(prefix in sku_name.upper() for prefix in ['AAD', 'ENTRA', 'EMS', 'IDENTITY']):
            license_info = {
                'sku_part_number': sku.sku_part_number,
                'sku_id': str(sku.sku_id),
                'enabled': sku.prepaid_units.enabled if sku.prepaid_units else 0,
                'consumed': sku.consumed_units,
                'available': (sku.prepaid_units.enabled - sku.consumed_units) if sku.prepaid_units else 0,
                'capability_status': sku.capability_status,
                'applies_to': sku.applies_to,
                'entra_service_plans': entra_plans
            }
            entra_licenses.append(license_info)
    
    # Calculate roles count from already-fetched data
    roles_count = len(directory_roles.value) if directory_roles.value else 0
    
    # Compile Entra information
    entra_info = {
        'tenant_id': org_details.id if org_details else None,
        'tenant_name': org_details.display_name if org_details else None,
        'verified_domains': [domain.name for domain in org_details.verified_domains] if org_details and org_details.verified_domains else [],
        'licenses': entra_licenses,
        'active_directory_roles': roles_count
    }
    
    return entra_info

async def get_entra_info(client, services_and_licenses=None, entra_client=None):
    """
    Get Entra information with enhanced observations.
    
    Args:
        client: Microsoft Graph client
        services_and_licenses: Shared data structure for license caching
        entra_client: Entra Client with cached identity & security data (optional)
    """
    try:
        # Use cached subscribed_skus if available
        if services_and_licenses:
            subscribed_skus = await services_and_licenses.get_raw_subscribed_skus()
            if subscribed_skus:
                org, directory_roles = await asyncio.gather(
                    client.organization.get(),
                    client.directory_roles.get()
                )
            else:
                org, subscribed_skus, directory_roles = await fetch_entra_data(client)
        else:
            org, subscribed_skus, directory_roles = await fetch_entra_data(client)
        
        entra_info = process_entra_data(org, subscribed_skus, directory_roles)
    except HttpResponseError as e:
        with _stdout_lock:
            if e.status_code == 403:
                print(f"[{get_timestamp()}] [WARNING]  Entra information: Insufficient permissions (requires admin role)")
            else:
                print(f"[{get_timestamp()}] [WARNING]  Entra information: HTTP {e.status_code}")
        return {
            'available': False,
            'reason': f'Insufficient permissions (HTTP {e.status_code})',
            'recommendations': []
        }
    
    recommendations = []
    
    # Append to shared data structure if provided
    if services_and_licenses:
        await services_and_licenses.append_service_data('entra', entra_info.get('licenses', []))
    
    # Create/ensure entra_client is available BEFORE generating recommendations
    if not entra_client:
        from get_entra_client import get_entra_client
        tenant_id = entra_info.get('tenant_id')
        entra_client = await get_entra_client(client, tenant_id)
    
    # Pre-compute entra insights once (similar to pp_insights pattern)
    from Recommendations.entra.entra_insights import extract_entra_insights_from_client
    entra_insights = extract_entra_insights_from_client(entra_client)
    
    # Track features already added to avoid duplicates
    added_features = set()
    
    for lic in entra_info.get('licenses', []):
        sku_name = lic.get('sku_part_number', 'Unknown')
        for plan in lic.get('entra_service_plans', []):
            plan_name = plan.get('name')
            
            # Only include if this feature actually belongs to entra service
            if determine_service_type(plan_name) != 'entra':
                continue
            
            # Skip if we've already added a recommendation for this service plan
            if plan_name in added_features:
                continue
            added_features.add(plan_name)
            
            status = plan.get('status', 'Success')
            
            # Generate recommendations - pass pre-computed entra_insights
            rec = get_recommendation('entra', plan_name, sku_name, status, client=client, entra_insights=entra_insights)
            
            # Handle both single recommendations and lists
            if isinstance(rec, list):
                recommendations.extend(rec)
            else:
                recommendations.append(rec)
    
    # Global Secure Access (Entra Internet Access) doesn't have a service plan
    # It's API-only, so manually invoke if we collected network access data
    if entra_insights and entra_insights.get('network_access_summary'):
        network_status = entra_insights['network_access_summary'].get('status')
        
        # Only invoke if we have data or meaningful error states
        if network_status in ['Success', 'NotLicensed', 'PermissionDenied']:
            # Import the recommendation function directly
            from Recommendations.entra.ENTRA_INTERNET_ACCESS import get_recommendation as get_gsa_recommendation
            
            # Use a generic SKU name since this feature isn't tied to a specific license
            gsa_recs = get_gsa_recommendation(
                sku_name='Microsoft Entra Suite',
                status='Success' if network_status == 'Success' else 'PendingActivation',
                entra_insights=entra_insights
            )
            
            # Handle both single recommendations and lists
            if isinstance(gsa_recs, list):
                recommendations.extend(gsa_recs)
            else:
                recommendations.append(gsa_recs)
    
    # Global Secure Access (Entra Private Access) - also API-only
    if entra_insights and entra_insights.get('private_access_summary'):
        private_status = entra_insights['private_access_summary'].get('status')
        
        if private_status in ['Success', 'NotLicensed', 'PermissionDenied']:
            from Recommendations.entra.ENTRA_PRIVATE_ACCESS import get_recommendation as get_private_access_recommendation
            
            private_recs = get_private_access_recommendation(
                sku_name='Microsoft Entra Suite',
                status='Success' if private_status == 'Success' else 'PendingActivation',
                entra_insights=entra_insights
            )
            
            if isinstance(private_recs, list):
                recommendations.extend(private_recs)
            else:
                recommendations.append(private_recs)
            
            # Conditional Access for Private Access (only if Private Access is configured)
            if private_status == 'Success':
                from Recommendations.entra.ENTRA_PRIVATE_ACCESS_CA import get_recommendation as get_private_ca_recommendation
                
                private_ca_rec = get_private_ca_recommendation(
                    sku_name='Microsoft Entra Suite',
                    status='Success',
                    entra_insights=entra_insights
                )
                
                if isinstance(private_ca_rec, list):
                    recommendations.extend(private_ca_rec)
                else:
                    recommendations.append(private_ca_rec)
    
    # Frontline Internet Access - only invoke if network access shows frontline capability
    # For now, we'll invoke it if Internet Access is available (could refine later)
    if entra_insights and entra_insights.get('network_access_summary'):
        network_status = entra_insights['network_access_summary'].get('status')
        
        if network_status == 'Success':
            from Recommendations.entra.ENTRA_INTERNET_ACCESS_FRONTLINE import get_recommendation as get_frontline_recommendation
            
            frontline_rec = get_frontline_recommendation(
                sku_name='Microsoft Entra Suite',
                status='Success',
                entra_insights=entra_insights
            )
            
            if isinstance(frontline_rec, list):
                recommendations.extend(frontline_rec)
            else:
                recommendations.append(frontline_rec)
    
    entra_info['recommendations'] = recommendations
    return entra_info

