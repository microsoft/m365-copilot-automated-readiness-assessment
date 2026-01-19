import asyncio
from get_recommendation import get_recommendation
import sys
from spinner import get_timestamp, _stdout_lock
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from service_categorization import determine_service_type

async def fetch_copilot_studio_licenses(client):
    """Fetch license data to check if Copilot Studio is licensed"""
    subscribed_skus = await client.subscribed_skus.get()
    return subscribed_skus

def get_copilot_studio_service_plans(subscribed_skus):
    """Get all Copilot Studio service plans from licenses with their status"""
    copilot_plans = []
    for sku in subscribed_skus.value:
        if sku.service_plans:
            sku_copilot_plans = []
            for plan in sku.service_plans:
                plan_name = plan.service_plan_name or ''
                # Use centralized service type determination
                if determine_service_type(plan_name) == 'copilot_studio':
                    sku_copilot_plans.append({
                        'name': plan_name,
                        'status': plan.provisioning_status or 'Unknown'
                    })
            
            if sku_copilot_plans:
                copilot_plans.append({
                    'sku_part_number': sku.sku_part_number,
                    'sku_id': str(sku.sku_id),
                    'service_plans': sku_copilot_plans
                })
    
    return copilot_plans

async def get_copilot_studio_info(client, services_and_licenses=None, pp_client=None):
    """Get Copilot Studio (Power Virtual Agents) service plan information
    
    Args:
        client: Microsoft Graph client
        services_and_licenses: Shared data structure for license caching
        pp_client: Power Platform Management API client (optional)
    """
    try:
        # Use cached data if available
        if services_and_licenses:
            subscribed_skus = await services_and_licenses.get_raw_subscribed_skus()
            if not subscribed_skus:
                subscribed_skus = await fetch_copilot_studio_licenses(client)
        else:
            subscribed_skus = await fetch_copilot_studio_licenses(client)
        
        copilot_plans = get_copilot_studio_service_plans(subscribed_skus)
    except HttpResponseError as e:
        with _stdout_lock:
            if e.status_code == 403:
                print(f"[{get_timestamp()}] ⚠️  Copilot Studio information: Insufficient permissions (requires admin role)")
            else:
                print(f"[{get_timestamp()}] ⚠️  Copilot Studio information: HTTP {e.status_code}")
        return {
            'available': False,
            'reason': f'Insufficient permissions (HTTP {e.status_code})',
            'has_copilot_studio': False,
            'recommendations': []
        }
    
    recommendations = []
    
    if not copilot_plans:
        return {
            'available': False,
            'reason': 'Copilot Studio features not found in current licenses',
            'has_copilot_studio': False,
            'note': 'Copilot Studio requires standalone license or included with M365 Copilot',
            'recommendations': recommendations
        }
    
    # Append to shared data structure if provided
    if services_and_licenses:
        await services_and_licenses.append_service_data('copilot_studio', copilot_plans)
    
    # PRE-COMPUTE Power Platform insights ONCE (instead of duplicating in every recommendation)
    # This extracts from already-cached pp_client data (no API calls)
    from get_power_platform_client import extract_pp_insights_from_client
    pp_insights = extract_pp_insights_from_client(pp_client) if pp_client else None
    
    # Check for all service plans and create recommendations (blank for Success)
    # Track features already added to avoid duplicates
    # Collect async tasks for parallel execution
    import inspect
    import asyncio
    async_tasks = []
    added_features = set()
    
    for lic in copilot_plans:
        sku_name = lic.get('sku_part_number', 'Unknown')
        for plan in lic.get('service_plans', []):
            plan_name = plan.get('name')
            # Skip if we've already added a recommendation for this service plan
            if plan_name in added_features:
                continue
            added_features.add(plan_name)
            
            status = plan.get('status', 'Success')
            # Generate recommendations for all service plans
            # Pass pre-computed pp_insights to avoid redundant extraction
            rec = get_recommendation('copilot_studio', plan_name, sku_name, status, client, pp_client, pp_insights)
            
            # Collect async tasks for parallel execution
            if inspect.iscoroutine(rec):
                async_tasks.append(rec)
            else:
                # Handle sync recommendations immediately
                if isinstance(rec, list):
                    recommendations.extend(rec)
                else:
                    recommendations.append(rec)
    
    # Run all async recommendations in parallel
    if async_tasks:
        results = await asyncio.gather(*async_tasks)
        for result in results:
            if isinstance(result, list):
                recommendations.extend(result)
            else:
                recommendations.append(result)
    
    return {
        'available': True,
        'has_copilot_studio': True,
        'licenses': copilot_plans,
        'total_licenses': len(copilot_plans),
        'recommendations': recommendations
    }

