"""
__init__.py for power_platform recommendations
Dynamically imports all recommendation modules
"""
import os
import importlib
import sys
from pathlib import Path
from spinner import get_timestamp, _stdout_lock

# Get all .py files in this directory except __init__.py
current_dir = Path(__file__).parent
recommendation_modules = {}

for file_path in current_dir.glob("*.py"):
    if file_path.name != "__init__.py":
        module_name = file_path.stem
        module = importlib.import_module(f"Recommendations.power_platform.{module_name}")
        # Store with uppercase key for case-insensitive lookup
        recommendation_modules[module_name.upper()] = module.get_recommendation

# Update progress bar
from module_loader import get_progress_tracker
get_progress_tracker().update('Power Platform', len(recommendation_modules))

def get_feature_recommendation(feature_name, sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Get recommendation for a specific feature
    
    Args:
        feature_name: Technical feature/service plan name (e.g., 'POWERAPPS_O365_P3')
        sku_name: SKU name where the feature is found
        status: Provisioning status of the feature
        client: Optional Graph client for deployment checks
        pp_client: Optional Power Platform client for deployment checks
        pp_insights: Pre-computed Power Platform insights (performance optimization)
    
    Returns:
        dict: Recommendation object
    """
    # Use uppercase for case-insensitive lookup
    if feature_name.upper() in recommendation_modules:
        func = recommendation_modules[feature_name.upper()]
        # Check if function accepts client parameter
        import inspect
        sig = inspect.signature(func)
        has_client_param = 'client' in sig.parameters
        has_pp_client_param = 'pp_client' in sig.parameters
        has_pp_insights_param = 'pp_insights' in sig.parameters
        
        # Handle async functions
        if inspect.iscoroutinefunction(func):
            import asyncio
            
            # Prepare coroutine with appropriate parameters
            if has_pp_insights_param:
                coro = func(sku_name, status, client=client, pp_client=pp_client, pp_insights=pp_insights)
            elif has_pp_client_param:
                coro = func(sku_name, status, client=client, pp_client=pp_client)
            elif has_client_param:
                coro = func(sku_name, status, client=client)
            else:
                coro = func(sku_name, status)
            
            # Check if we're in a running event loop
            try:
                asyncio.get_running_loop()
                # We're in an async context - return coroutine for caller to await
                return coro
            except RuntimeError:
                # No running loop - safe to use asyncio.run()
                result = asyncio.run(coro)
        else:
            # Handle sync functions
            if has_pp_insights_param:
                result = func(sku_name, status, client=client, pp_client=pp_client, pp_insights=pp_insights)
            elif has_pp_client_param:
                result = func(sku_name, status, client=client, pp_client=pp_client)
            elif has_client_param:
                result = func(sku_name, status, client=client)
            else:
                result = func(sku_name, status)
        
        # Handle functions that return lists of recommendations
        if isinstance(result, list):
            return result
        return result
    
    # Fallback for features without specific recommendations
    from friendly_names import get_friendly_plan_name
    from new_recommendation import new_recommendation
    from friendly_names import get_friendly_sku_name
    
    friendly_name = get_friendly_plan_name(feature_name)
    friendly_sku = get_friendly_sku_name(sku_name)
    if status == "Success":
        return new_recommendation(
            service="Power Platform",
            feature=friendly_name,
            observation=f"{friendly_name} is active in {friendly_sku}, enabling low-code automation and agent extensions",
            recommendation="",
            link_text="Power Platform Documentation",
            link_url="https://learn.microsoft.com/power-platform/",
            status=status
        )
    
    # Enhanced recommendations for missing/disabled Power Platform features
    if status == "PendingActivation":
        obs = f"{friendly_name} is pending activation in {friendly_sku}. M365 Copilot agents require Power Platform for custom actions and workflow automation"
        rec = f"Complete activation of {friendly_name} to enable M365 Copilot agents to trigger Power Automate flows, access Dataverse, and execute custom business logic"
        priority = "Medium"
    elif status == "Disabled":
        obs = f"{friendly_name} is disabled in {friendly_sku}, preventing M365 Copilot from extending capabilities with custom apps and automated workflows"
        rec = f"Enable {friendly_name} to allow M365 Copilot agents to integrate with Power Apps, execute automated workflows, and access business data through low-code extensions"
        priority = "Medium"
    else:  # PendingInput, Suspended, Warning, etc.
        obs = f"{friendly_name} has status '{status}' in {friendly_sku}, limiting M365 Copilot's ability to leverage Power Platform for agent extensibility"
        rec = f"Resolve the '{status}' status for {friendly_name} to unlock custom agent actions, workflow automation, and business process integration for M365 Copilot"
        priority = "Medium"
    
    return new_recommendation(
        service="Power Platform",
        feature=friendly_name,
        observation=obs,
        recommendation=rec,
        link_text="Power Platform Documentation",
        link_url="https://learn.microsoft.com/power-platform/",
        priority=priority,
        status=status
    )
