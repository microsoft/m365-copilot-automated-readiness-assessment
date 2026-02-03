import asyncio
from .get_power_platform_client import get_power_platform_client
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from .get_recommendation import get_recommendation
import sys
from .spinner import get_timestamp, _stdout_lock
from .service_categorization import determine_service_type

async def fetch_power_platform_licenses(client):
    """Fetch license data to check if Power Platform is licensed"""
    subscribed_skus = await client.subscribed_skus.get()
    return subscribed_skus

def get_power_platform_service_plans(subscribed_skus):
    """Get all Power Platform service plans from licenses"""
    pp_plans = []
    for sku in subscribed_skus.value:
        if sku.service_plans:
            sku_pp_plans = []
            for plan in sku.service_plans:
                plan_name = plan.service_plan_name or ''
                # Use centralized service type determination
                # Power Platform plans should not include Copilot Studio (it has its own category)
                service_type = determine_service_type(plan_name)
                if service_type == 'power_platform':
                    sku_pp_plans.append({
                        'name': plan_name,
                        'status': plan.provisioning_status or 'Unknown'
                    })
            
            if sku_pp_plans:
                pp_plans.append({
                    'sku_part_number': sku.sku_part_number,
                    'sku_id': str(sku.sku_id),
                    'service_plans': sku_pp_plans
                })
    
    return pp_plans

def process_power_platform_environments(pp_client):
    """Process cached Power Platform environment data from client"""
    if not hasattr(pp_client, 'environments'):
        return {
            'available': False,
            'reason': 'Environment data not cached on client',
            'has_power_platform': False,
            'note': 'Client may not have been properly initialized'
        }
    
    environments = pp_client.environments
    
    return {
        'available': True,
        'total_environments': len(environments),
        'environments': [
            {
                'name': env.get('properties', {}).get('displayName'),
                'type': env.get('properties', {}).get('environmentSku'),
                'location': env.get('location'),
                'state': env.get('properties', {}).get('states', {}).get('management', {}).get('id')
            }
            for env in environments
        ],
        'has_power_platform': True
    }

async def get_power_platform_info(client, services_and_licenses=None, pp_client=None):
    """Get Power Platform information
    
    Args:
        client: Microsoft Graph client
        services_and_licenses: Shared data structure for license caching
        pp_client: Power Platform Management API client (optional)
    """
    # Use cached data if available
    if services_and_licenses:
        subscribed_skus = await services_and_licenses.get_raw_subscribed_skus()
        if not subscribed_skus:
            subscribed_skus = await fetch_power_platform_licenses(client)
    else:
        subscribed_skus = await fetch_power_platform_licenses(client)
    
    pp_plans = get_power_platform_service_plans(subscribed_skus)
    
    recommendations = []
    
    if not pp_plans:
        return {
            'available': False,
            'reason': 'Power Platform features not found in current licenses',
            'has_power_platform': False,
            'note': 'Power Platform requires M365 licenses with seeded plans or standalone licenses',
            'recommendations': recommendations
        }
    
    # Append to shared data structure if provided
    if services_and_licenses:
        await services_and_licenses.append_service_data('power_platform', pp_plans)
    
    # Create/ensure pp_client is available BEFORE generating recommendations
    # Recommendations need pp_client for data-driven insights
    pp_client_created = False
    if pp_client is None:
        pp_client = await get_power_platform_client()
        pp_client_created = True
    
    # PRE-COMPUTE Power Platform insights ONCE (instead of duplicating in every recommendation)
    # This extracts from already-cached pp_client data (no API calls)
    from .get_power_platform_client import extract_pp_insights_from_client
    pp_insights = extract_pp_insights_from_client(pp_client) if pp_client else None
    
    # Check for all service plans and create recommendations (blank for Success)
    # Track features already added to avoid duplicates
    # Collect async tasks for parallel execution
    import inspect
    import asyncio
    async_tasks = []
    added_features = set()
    
    for lic in pp_plans:
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
            rec = get_recommendation('power_platform', plan_name, sku_name, status, client, pp_client, pp_insights)
            
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
    
    # Check if pp_client is available for environment data and pseudo-features
    try:
        if pp_client is None:
            # Client creation failed (no admin access)
            return {
                'available': False,
                'reason': 'Power Platform is licensed but API access denied. Requires Power Platform admin role.',
                'has_power_platform': False,
                'note': 'Access requires Power Platform Administrator or Global Administrator role',
                'licenses': pp_plans,
                'total_licenses': len(pp_plans),
                'recommendations': recommendations
            }
        
        # Use cached environment data from client (already fetched during client initialization)
        result = process_power_platform_environments(pp_client)
        
        # Add pseudo-feature recommendations for governance and AI capabilities
        # These run once per tenant, not per service plan
        # IMPORTANT: Must run AFTER pp_client is created to access DLP/AI Builder data
        import inspect
        pseudo_features = ['DLP_GOVERNANCE', 'AI_BUILDER_MODELS']
        for pseudo_feature in pseudo_features:
            # Pass first SKU as placeholder (these aren't tied to specific licenses)
            placeholder_sku = pp_plans[0].get('sku_part_number', 'Unknown') if pp_plans else 'Unknown'
            rec = get_recommendation('power_platform', pseudo_feature, placeholder_sku, 'Success', client, pp_client, pp_insights)
            
            if inspect.iscoroutine(rec):
                rec = await rec
            
            if isinstance(rec, list):
                recommendations.extend(rec)
            elif rec:  # May return None or empty
                recommendations.append(rec)
        
        # Only close if we created it
        if pp_client_created:
            await pp_client.aclose()
        
        # Add license information to the result
        result['licenses'] = pp_plans
        result['total_licenses'] = len(pp_plans)
        result['recommendations'] = recommendations
        return result
            
    except (HttpResponseError, ClientAuthenticationError) as e:
        # Only close if we created it
        if pp_client_created and pp_client:
            await pp_client.aclose()
        
        status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        
        if status_code == 403:
            reason = 'Power Platform is licensed but API access denied. Requires Power Platform admin role.'
        elif status_code == 401:
            reason = 'Power Platform is licensed but authentication failed.'
        else:
            reason = 'Power Platform is licensed but API access error occurred.'
        
        return {
            'available': False,
            'reason': reason,
            'has_power_platform': False,
            'note': 'Access requires Power Platform Administrator or Global Administrator role',
            'licenses': pp_plans,
            'total_licenses': len(pp_plans),
            'recommendations': recommendations
        }
    except Exception as e:
        # Only close if we created it
        if pp_client_created and pp_client:
            await pp_client.aclose()
        return {
            'available': False,
            'reason': f'Power Platform is licensed but unexpected error: {type(e).__name__}',
            'has_power_platform': False,
            'error': str(e),
            'licenses': pp_plans,
            'total_licenses': len(pp_plans),
            'recommendations': recommendations
        }
