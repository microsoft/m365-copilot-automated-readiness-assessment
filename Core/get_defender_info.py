import asyncio
from .get_recommendation import get_recommendation
from .service_categorization import determine_service_type
from Recommendations.defender.defender_insights import DefenderInsights
import sys
from .spinner import get_timestamp, _stdout_lock
from azure.core.exceptions import HttpResponseError

async def fetch_defender_licenses(client):
    """Fetch license data to check if Defender is licensed"""
    subscribed_skus = await client.subscribed_skus.get()
    return subscribed_skus

def get_defender_service_plans(subscribed_skus):
    """Get all Defender service plans from licenses with their status"""
    # Use specific patterns to match determine_service_type
    defender_keywords = ['DEFENDER', 'ATP', 'THREAT', 'WINDEFATP', 'ATA', 'SAFEDOCS',
                        'ADALLOM', 'EOP_', 'M365_LIGHTHOUSE', 'MTP']
    
    defender_plans = []
    for sku in subscribed_skus.value:
        if sku.service_plans:
            sku_defender_plans = []
            for plan in sku.service_plans:
                plan_name = plan.service_plan_name or ''
                plan_upper = plan_name.upper()
                # Check substring keywords
                is_defender = any(keyword in plan_upper for keyword in defender_keywords)
                
                if is_defender:
                    sku_defender_plans.append({
                        'name': plan_name,
                        'status': plan.provisioning_status or 'Unknown'
                    })
            
            if sku_defender_plans:
                defender_plans.append({
                    'sku_part_number': sku.sku_part_number,
                    'sku_id': str(sku.sku_id),
                    'service_plans': sku_defender_plans
                })
    
    return defender_plans

async def get_defender_info(client, defender_client=None, services_and_licenses=None, purview_client=None):
    """Get Microsoft Defender service plan information
    
    Args:
        client: Microsoft Graph client
        defender_client: Optional Defender API client with security metrics
        services_and_licenses: Optional cached license data
        purview_client: Optional Purview client for data governance assessment
    
    Returns:
        Dictionary with Defender availability, licenses, and recommendations
    """
    try:
        # Use cached data if available
        if services_and_licenses:
            subscribed_skus = await services_and_licenses.get_raw_subscribed_skus()
            if not subscribed_skus:
                subscribed_skus = await fetch_defender_licenses(client)
        else:
            subscribed_skus = await fetch_defender_licenses(client)
        
        defender_plans = get_defender_service_plans(subscribed_skus)
    
    except HttpResponseError as e:
        with _stdout_lock:
            if e.status_code == 403:
                print(f"[{get_timestamp()}] ⚠️  Defender information: Insufficient permissions (requires admin role)")
            else:
                print(f"[{get_timestamp()}] ⚠️  Defender information: HTTP {e.status_code}")
        return {
            'available': False,
            'reason': f'Insufficient permissions (HTTP {e.status_code})',
            'has_defender': False,
            'recommendations': []
        }
    
    recommendations = []
    
    if not defender_plans:
        return {
            'available': False,
            'reason': 'Microsoft Defender features not found in current licenses',
            'has_defender': False,
            'note': 'Defender requires M365 Business Premium, E3, E5 or standalone licenses',
            'recommendations': recommendations
        }
    
    # Pre-compute defender insights once (similar to pp_insights pattern)
    defender_insights = DefenderInsights(defender_client) if defender_client else None
    
    # Append to shared data structure if provided
    if services_and_licenses:
        await services_and_licenses.append_service_data('defender', defender_plans)
    
    # Check for XDR status - add recommendation for activation or missing license
    # This handles both:
    # - Tenants with XDR license but not activated
    # - Tenants without XDR license who should upgrade
    from Recommendations.defender.DEFENDER_XDR_ACTIVATION import get_recommendation as get_activation_rec
    xdr_recommendation = get_activation_rec(defender_client, defender_plans)
    if xdr_recommendation:
        recommendations.append(xdr_recommendation)
    
    # Check for Defender for Endpoint device onboarding status
    # This replaces console warnings with an actionable recommendation
    # when API returns 403 due to no devices onboarded
    from Recommendations.defender.DEFENDER_ENDPOINT_ONBOARDING import get_recommendation as get_onboarding_rec
    onboarding_recommendation = await get_onboarding_rec(client, defender_client, services_and_licenses, purview_client)
    if onboarding_recommendation:
        recommendations.append(onboarding_recommendation)
    
    # Check for all service plans and create recommendations (blank for Success)
    # Track features already added to avoid duplicates
    # Collect async tasks for parallel execution
    import inspect
    import asyncio
    async_tasks = []
    added_features = set()
    
    for lic in defender_plans:
        sku_name = lic.get('sku_part_number', 'Unknown')
        for plan in lic.get('service_plans', []):
            plan_name = plan.get('name')
            
            # Only include if this feature actually belongs to defender service
            if determine_service_type(plan_name) != 'defender':
                continue
            
            # Skip if we've already added a recommendation for this service plan
            if plan_name in added_features:
                continue
            added_features.add(plan_name)
            
            status = plan.get('status', 'Success')
            # Generate recommendations for all service plans
            # Pass defender_client and defender_insights to enable API data enrichment
            rec = get_recommendation('defender', plan_name, sku_name, status, client=client, defender_client=defender_client, defender_insights=defender_insights)
            
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
    
    # ========== COPILOT-SPECIFIC RECOMMENDATIONS ==========
    # Generate cross-cutting Copilot security assessments that leverage
    # Defender threat intelligence and Purview data governance
    
    # 1. Copilot Security Posture - Overall readiness assessment
    from Recommendations.defender.COPILOT_SECURITY_POSTURE import get_recommendation as get_security_posture
    copilot_security_posture = get_security_posture(defender_client, purview_client)
    if copilot_security_posture:
        recommendations.append(copilot_security_posture)
    
    # 2. Copilot Threat Intelligence - Advanced Hunting insights
    from Recommendations.defender.COPILOT_THREAT_INTELLIGENCE import get_recommendation as get_threat_intel
    copilot_threat_intel = get_threat_intel(defender_client)
    if copilot_threat_intel:
        recommendations.append(copilot_threat_intel)
    
    # 3. Copilot Data Governance - Purview compliance assessment
    from Recommendations.defender.COPILOT_DATA_GOVERNANCE import get_recommendation as get_data_governance
    copilot_data_governance = get_data_governance(purview_client, defender_client)
    if copilot_data_governance:
        recommendations.append(copilot_data_governance)
    
    return {
        'available': True,
        'has_defender': True,
        'licenses': defender_plans,
        'total_licenses': len(defender_plans),
        'recommendations': recommendations
    }

