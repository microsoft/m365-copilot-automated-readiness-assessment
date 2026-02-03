import asyncio
from .get_recommendation import get_recommendation
from .service_categorization import determine_service_type
from .get_purview_client import get_purview_client
import sys
from .spinner import get_timestamp, _stdout_lock
from azure.core.exceptions import HttpResponseError

async def fetch_purview_licenses(client):
    """Fetch license data to check if Purview is licensed"""
    subscribed_skus = await client.subscribed_skus.get()
    return subscribed_skus

def get_purview_service_plans(subscribed_skus):
    """Get all Purview/Compliance service plans from licenses"""
    purview_keywords = ['PURVIEW', 'COMPLIANCE', 'INFORMATION_PROTECTION', 'DLP', 'COMMUNICATIONS_COMPLIANCE',
                       'RECORDS_MANAGEMENT', 'INFO_GOVERNANCE', 'INSIDER_RISK', 'PREMIUM_ENCRYPTION',
                       'DATA_INVESTIGATIONS', 'EQUIVIO', 'LOCKBOX', 'CUSTOMER_KEY', 'CONTENTEXPLORER',
                       'INFORMATION_BARRIERS', 'RMS_', 'AIP_', 'PAM_', 'M365_AUDIT', 'EDISCOVERY',
                       'M365_ADVANCED_AUDITING', 'MIP_S_', 'ML_CLASSIFICATION', 'CONTENT_EXPLORER', 'FORMS_PLAN']
    
    purview_plans = []
    for sku in subscribed_skus.value:
        if sku.service_plans:
            sku_purview_plans = []
            for plan in sku.service_plans:
                plan_name = plan.service_plan_name or ''
                if any(keyword in plan_name.upper() for keyword in purview_keywords):
                    sku_purview_plans.append({
                        'name': plan_name,
                        'status': plan.provisioning_status or 'Unknown'
                    })
            
            if sku_purview_plans:
                purview_plans.append({
                    'sku_part_number': sku.sku_part_number,
                    'sku_id': str(sku.sku_id),
                    'service_plans': sku_purview_plans
                })
    
    return purview_plans

async def get_purview_info(client, services_and_licenses=None, purview_client=None):
    """Get Microsoft Purview compliance service plan information
    
    Args:
        client: Microsoft Graph client
        services_and_licenses: Shared data structure for license caching
        purview_client: Purview deployment data client (optional)
    """
    try:
        # Use cached data if available
        if services_and_licenses:
            subscribed_skus = await services_and_licenses.get_raw_subscribed_skus()
            if not subscribed_skus:
                subscribed_skus = await fetch_purview_licenses(client)
        else:
            subscribed_skus = await fetch_purview_licenses(client)
        
        purview_plans = get_purview_service_plans(subscribed_skus)
    except HttpResponseError as e:
        with _stdout_lock:
            if e.status_code == 403:
                print(f"[{get_timestamp()}] [WARNING]  Purview information: Insufficient permissions (requires admin role)")
            else:
                print(f"[{get_timestamp()}] [WARNING]  Purview information: HTTP {e.status_code}")
        return {
            'available': False,
            'reason': f'Insufficient permissions (HTTP {e.status_code})',
            'has_purview': False,
            'recommendations': []
        }
    
    recommendations = []
    
    if not purview_plans:
        return {
            'available': False,
            'reason': 'Microsoft Purview compliance features not found in current licenses',
            'has_purview': False,
            'note': 'Purview requires M365 E5, E5 Compliance, or standalone licenses',
            'recommendations': recommendations
        }
    
    # Append to shared data structure if provided
    if services_and_licenses:
        await services_and_licenses.append_service_data('purview', purview_plans)
    
    # Purview_client is now provided by orchestrator (initialized before service gathering)
    # No need to create it here - it's optional for deployment-aware recommendations
    
    # Check for all service plans and create recommendations (blank for Success)
    # Track features already added to avoid duplicates
    # Collect async tasks for parallel execution
    import inspect
    async_tasks = []
    added_features = set()
    
    for lic in purview_plans:
        sku_name = lic.get('sku_part_number', 'Unknown')
        for plan in lic.get('service_plans', []):
            plan_name = plan.get('name')
            
            # Only include if this feature actually belongs to purview service
            if determine_service_type(plan_name) != 'purview':
                continue
            
            # Skip if we've already added a recommendation for this service plan
            if plan_name in added_features:
                continue
            added_features.add(plan_name)
            
            status = plan.get('status', 'Success')
            # Generate recommendations for all service plans
            # Pass purview_client to enable deployment-aware recommendations
            rec = get_recommendation('purview', plan_name, sku_name, status, client=client, purview_client=purview_client)
            
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
    
    # Build response with deployment data if available
    response = {
        'available': True,
        'has_purview': True,
        'licenses': purview_plans,
        'total_licenses': len(purview_plans),
        'recommendations': recommendations
    }
    
    # Add deployment data if purview_client is available
    if purview_client:
        response['deployment'] = {
            'sensitivity_labels': purview_client.sensitivity_labels,
            'retention_labels': purview_client.retention_labels,
            'retention_events': purview_client.retention_events,
            'retention_event_types': purview_client.retention_event_types,
            'information_barriers': purview_client.information_barriers,
            'ediscovery_cases': purview_client.ediscovery_cases,
            'dlp_policies': purview_client.dlp_policies,
            'dlp_alerts': purview_client.dlp_alerts,
            'irm_alerts': purview_client.irm_alerts,
            'comm_compliance': purview_client.comm_compliance,
            'audit_logs': purview_client.audit_logs,
            'customer_lockbox': purview_client.customer_lockbox,
            'total_endpoints_available': purview_client.total_endpoints_available
        }
    
    return response

