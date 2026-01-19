from get_recommendation import get_recommendation
import sys
from spinner import get_timestamp, _stdout_lock
from azure.core.exceptions import HttpResponseError
from service_categorization import determine_service_type
from get_m365_client import extract_m365_insights_from_client

def process_m365_licenses(subscribed_skus):
    """Process M365 license data into structured format"""
    license_info = []
    for sku in subscribed_skus.value:
        # Process service plans with status
        service_plans = []
        if sku.service_plans:
            for plan in sku.service_plans:
                service_plans.append({
                    'name': plan.service_plan_name,
                    'status': plan.provisioning_status or 'Unknown'
                })
        
        info = {
            'sku_part_number': sku.sku_part_number,
            'sku_id': str(sku.sku_id),
            'enabled': sku.prepaid_units.enabled if sku.prepaid_units else 0,
            'consumed': sku.consumed_units,
            'available': (sku.prepaid_units.enabled - sku.consumed_units) if sku.prepaid_units else 0,
            'service_plans': service_plans
        }
        license_info.append(info)
    return license_info

async def get_m365_info(client, services_and_licenses=None, m365_client=None):
    """Get M365 license information
    
    Args:
        client: Graph API client
        services_and_licenses: Optional services container for caching
        m365_client: Optional pre-initialized M365 client with usage data
    """
    try:
        # Use cached data if available, otherwise fetch
        if services_and_licenses:
            subscribed_skus = await services_and_licenses.get_raw_subscribed_skus()
            if not subscribed_skus:
                subscribed_skus = await client.subscribed_skus.get()
        else:
            subscribed_skus = await client.subscribed_skus.get()
        
        license_info = process_m365_licenses(subscribed_skus)
    except HttpResponseError as e:
        with _stdout_lock:
            if e.status_code == 403:
                print(f"[{get_timestamp()}] [WARNING]  M365 service plans: Insufficient permissions (requires admin role)")
            else:
                print(f"[{get_timestamp()}] [WARNING]  M365 service plans: HTTP {e.status_code}")
        return ([], [])
    
    # Extract M365 insights once for all recommendations
    m365_insights = None
    if m365_client:
        m365_insights = extract_m365_insights_from_client(m365_client)
    
    recommendations = []
    
    # Append to shared data structure if provided
    if services_and_licenses:
        await services_and_licenses.append_service_data('m365', license_info)
    
    # Check for all service plans and create recommendations (blank for Success)
    # Track features already added to avoid duplicates
    # Collect async tasks for parallel execution
    import inspect
    import asyncio
    async_tasks = []
    added_features = set()
    
    for lic in license_info:
        sku_name = lic.get('sku_part_number', 'Unknown')
        for plan in lic.get('service_plans', []):
            status = plan.get('status', 'Success')
            plan_name = plan.get('name', '')
            
            # Skip features that belong to other services (they handle their own)
            service_type = determine_service_type(plan_name)
            if service_type != 'm365':
                continue
            
            # Skip if we've already added a recommendation for this service plan
            if plan_name in added_features:
                continue
            added_features.add(plan_name)
            
            # Generate recommendations only for M365-specific features
            rec = get_recommendation('m365', plan_name, sku_name, status, client, m365_insights=m365_insights)
            
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
    
    return license_info, recommendations
