"""
__init__.py for entra recommendations
Dynamically imports all recommendation modules
"""
import os
import importlib
import sys
from pathlib import Path
from Core.spinner import get_timestamp, _stdout_lock

# Get all .py files in this directory except __init__.py and helper modules
current_dir = Path(__file__).parent
recommendation_modules = {}

for file_path in current_dir.glob("*.py"):
    if file_path.name not in ["__init__.py", "entra_insights.py"]:
        module_name = file_path.stem
        module = importlib.import_module(f"Recommendations.entra.{module_name}")
        # Store with uppercase key for case-insensitive lookup
        recommendation_modules[module_name.upper()] = module.get_recommendation

# Update progress bar
from Core.module_loader import get_progress_tracker
get_progress_tracker().update('Entra', len(recommendation_modules))

def get_feature_recommendation(feature_name, sku_name, status="Success", client=None, entra_insights=None):
    """
    Get recommendation for a specific feature
    
    Args:
        feature_name: Technical feature/service plan name (e.g., 'AAD_PREMIUM')
        sku_name: SKU name where the feature is found
        status: Provisioning status of the feature
        client: Optional Graph client for deployment checks
        entra_insights: Optional dict with pre-computed identity metrics
    
    Returns:
        dict: Recommendation object
    """
    # Use uppercase for case-insensitive lookup
    if feature_name.upper() in recommendation_modules:
        func = recommendation_modules[feature_name.upper()]
        # Check if function accepts client/entra_insights parameters
        import inspect
        sig = inspect.signature(func)
        has_client_param = 'client' in sig.parameters
        has_entra_insights_param = 'entra_insights' in sig.parameters
        
        # Handle async functions
        if inspect.iscoroutinefunction(func):
            import asyncio
            
            # Prepare coroutine with available parameters
            kwargs = {'sku_name': sku_name, 'status': status}
            if has_client_param:
                kwargs['client'] = client
            if has_entra_insights_param:
                kwargs['entra_insights'] = entra_insights
            
            coro = func(**kwargs)
            
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
            kwargs = {'sku_name': sku_name, 'status': status}
            if has_client_param:
                kwargs['client'] = client
            if has_entra_insights_param:
                kwargs['entra_insights'] = entra_insights
            
            result = func(**kwargs)
        
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
            service="Entra",
            feature=friendly_name,
            observation=f"{friendly_name} is active in {friendly_sku}, securing identity and access for Copilot users",
            recommendation="",
            link_text="Entra ID Documentation",
            link_url="https://learn.microsoft.com/entra/identity/",
            status=status
        )
    
    return new_recommendation(
        service="Entra",
        feature=friendly_name,
        observation=f"{friendly_name} is {status} in {friendly_sku}, limiting identity protection for AI adoption",
        recommendation=f"Enable {friendly_name} to provide identity governance, conditional access, and authentication controls that protect Copilot access and ensure secure AI adoption.",
        link_text="Entra ID Documentation",
        link_url="https://learn.microsoft.com/entra/identity/",
        priority="Medium",
        status=status
    )
