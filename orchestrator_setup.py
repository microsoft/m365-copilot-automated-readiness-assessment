"""Initialization and setup functions for orchestrator."""

from get_graph_client import get_graph_client
from services_and_licenses import ServicesAndLicenses
from spinner import get_timestamp


async def load_modules_and_analyze(tenant_id, service_config):
    """Load recommendation modules and analyze service plans.
    
    Args:
        tenant_id: Azure tenant ID
        service_config: Dict with run_* flags from validate_and_prepare_services()
    """
    # Initialize progress bar with actual count
    from module_loader import start_module_loading
    start_module_loading(service_config['services_to_load'])
    
    # Pre-load recommendation modules for selected services
    if service_config['run_m365']:
        import Recommendations.m365
    if service_config['run_entra']:
        import Recommendations.entra
    if service_config['run_defender']:
        import Recommendations.defender
    if service_config['run_purview']:
        import Recommendations.purview
    if service_config['run_power_platform']:
        import Recommendations.power_platform
    if service_config['run_copilot_studio']:
        import Recommendations.copilot_studio
    
    # Show feature analysis after modules are loaded
    from check_all_service_plans import analyze_service_plans
    await analyze_service_plans(tenant_id, service_config['services'])
    
    # Print start message after modules are loaded
    if service_config['run_all']:
        print(f"[{get_timestamp()}] 🚀 Starting orchestration for all services...")
    else:
        print(f"[{get_timestamp()}] 🚀 Starting orchestration for: {', '.join(service_config['services'])}...")


async def setup_graph_and_licenses(tenant_id, show_graph_messages):
    """Initialize Microsoft Graph client and ServicesAndLicenses container.
    
    Args:
        tenant_id: Azure tenant ID
        show_graph_messages: Whether to print Graph connection messages
        
    Returns:
        Tuple: (graph_client, services_and_licenses, has_license_data)
    """
    # Always create Graph client (needed for license checks in all services)
    # Use silent mode for PowerShell-only runs (Purview, Power Platform)
    client = await get_graph_client(tenant_id, silent=not show_graph_messages)
    if show_graph_messages:
        print(f"[{get_timestamp()}] ✅ Connected to Microsoft Graph (Service Principal)")
    
    # Setup services container (needed by all pipelines)
    services_and_licenses = ServicesAndLicenses()
    has_license_data = False
    try:
        subscribed_skus = await client.subscribed_skus.get()
        if subscribed_skus:
            await services_and_licenses.set_raw_subscribed_skus(subscribed_skus)
            has_license_data = True
    except Exception as e:
        pass
    
    return client, services_and_licenses, has_license_data
