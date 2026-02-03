"""
__init__.py for purview recommendations
Dynamically imports all recommendation modules
"""
import os
import importlib
import sys
from pathlib import Path
from Core.spinner import get_timestamp, _stdout_lock

# Get all .py files in this directory except __init__.py
current_dir = Path(__file__).parent
recommendation_modules = {}

for file_path in current_dir.glob("*.py"):
    if file_path.name != "__init__.py":
        module_name = file_path.stem
        module = importlib.import_module(f"Recommendations.purview.{module_name}")
        # Store with uppercase key for case-insensitive lookup
        recommendation_modules[module_name.upper()] = module.get_recommendation

# Update progress bar
from Core.module_loader import get_progress_tracker
get_progress_tracker().update('Purview', len(recommendation_modules))

def get_feature_recommendation(feature_name, sku_name, status="Success", client=None, purview_client=None):
    """
    Get recommendation for a specific feature
    
    Args:
        feature_name: Technical feature/service plan name (e.g., 'MIP_S_CLP2')
        sku_name: SKU name where the feature is found
        status: Provisioning status of the feature
        client: Optional Graph client for deployment checks
        purview_client: Optional Purview client with deployment data
    
    Returns:
        dict: Recommendation object
    """
    # Use uppercase for case-insensitive lookup
    if feature_name.upper() in recommendation_modules:
        func = recommendation_modules[feature_name.upper()]
        # Check if function accepts client and purview_client parameters
        import inspect
        sig = inspect.signature(func)
        has_client_param = 'client' in sig.parameters
        has_purview_client_param = 'purview_client' in sig.parameters
        
        # Handle async functions
        if inspect.iscoroutinefunction(func):
            import asyncio
            
            # Prepare coroutine with appropriate parameters
            if has_purview_client_param:
                coro = func(sku_name, status, client=client, purview_client=purview_client)
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
            if has_purview_client_param:
                result = func(sku_name, status, client=client, purview_client=purview_client)
            elif has_client_param:
                result = func(sku_name, status, client=client)
            else:
                result = func(sku_name, status)
        
        # Handle functions that return lists of recommendations
        if isinstance(result, list):
            return result
        return result
    
    # Fallback for features without specific recommendations
    from Core.friendly_names import get_friendly_plan_name
    from Core.new_recommendation import new_recommendation
    from Core.friendly_names import get_friendly_sku_name
    
    friendly_name = get_friendly_plan_name(feature_name)
    friendly_sku = get_friendly_sku_name(sku_name)
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=friendly_name,
            observation=f"{friendly_name} is active in {friendly_sku}, governing data that Copilot accesses and processes",
            recommendation="",
            link_text="Microsoft Purview Documentation",
            link_url="https://learn.microsoft.com/purview/",
            status=status
        )
    
    # Enhanced recommendations for missing/disabled Purview features
    if status == "PendingActivation":
        obs = f"{friendly_name} is pending activation in {friendly_sku}. M365 Copilot processes sensitive data that requires compliance governance"
        rec = f"Complete activation of {friendly_name} to ensure M365 Copilot responses comply with data retention, classification, and regulatory requirements"
        priority = "High"
    elif status == "Disabled":
        obs = f"{friendly_name} is disabled in {friendly_sku}, preventing proper governance of sensitive data that M365 Copilot accesses and generates"
        rec = f"Enable {friendly_name} to implement data loss prevention, sensitivity labels, and retention policies that control how M365 Copilot handles organizational knowledge and regulatory data"
        priority = "High"
    else:  # PendingInput, Suspended, Warning, etc.
        obs = f"{friendly_name} has status '{status}' in {friendly_sku}, creating compliance risks for M365 Copilot's data handling"
        rec = f"Resolve the '{status}' status for {friendly_name} to ensure M365 Copilot operates under proper compliance controls for data classification, retention, and regulatory adherence"
        priority = "High"  # Compliance is critical for enterprise AI
    
    return new_recommendation(
        service="Purview",
        feature=friendly_name,
        observation=obs,
        recommendation=rec,
        link_text="Microsoft Purview Documentation",
        link_url="https://learn.microsoft.com/purview/",
        priority=priority,
        status=status
    )
