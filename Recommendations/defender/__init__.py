"""
__init__.py for defender recommendations
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
    if file_path.name not in ["__init__.py", "defender_insights.py"]:
        module_name = file_path.stem
        module = importlib.import_module(f"Recommendations.defender.{module_name}")
        # Store with uppercase key for case-insensitive lookup
        recommendation_modules[module_name.upper()] = module.get_recommendation

# Update progress bar
from Core.module_loader import get_progress_tracker
get_progress_tracker().update('Defender', len(recommendation_modules))

def get_feature_recommendation(feature_name, sku_name, status="Success", client=None, defender_client=None, defender_insights=None):
    """
    Get recommendation for a specific feature
    
    Args:
        feature_name: Technical feature/service plan name (e.g., 'WINDEFATP')
        sku_name: SKU name where the feature is found
        status: Provisioning status of the feature
        client: Optional Graph client for deployment checks
        defender_client: Optional Defender API client with security metrics
        defender_insights: Optional DefenderInsights instance with pre-computed metrics
    
    Returns:
        dict: Recommendation object
    """
    # Use uppercase for case-insensitive lookup
    if feature_name.upper() in recommendation_modules:
        func = recommendation_modules[feature_name.upper()]
        # Check if function accepts client/defender_client/defender_insights parameters
        import inspect
        sig = inspect.signature(func)
        has_client_param = 'client' in sig.parameters
        has_defender_client_param = 'defender_client' in sig.parameters
        has_defender_insights_param = 'defender_insights' in sig.parameters
        
        # Handle async functions
        if inspect.iscoroutinefunction(func):
            import asyncio
            
            # Prepare coroutine with available parameters
            kwargs = {'sku_name': sku_name, 'status': status}
            if has_client_param:
                kwargs['client'] = client
            if has_defender_client_param:
                kwargs['defender_client'] = defender_client
            if has_defender_insights_param:
                kwargs['defender_insights'] = defender_insights
            
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
            if has_defender_client_param:
                kwargs['defender_client'] = defender_client
            if has_defender_insights_param:
                kwargs['defender_insights'] = defender_insights
            
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
        # Base observation (license check)
        base_observation = f"{friendly_name} is active in {friendly_sku}, protecting Copilot workloads"
        base_recommendation = ""
        
        # Enrich with defender_client data if available (use Graph Security even without devices)
        additional_insights = []
        
        if defender_client:
            # Feature-specific enrichment based on available Defender data
            if feature_name.upper() == "WINDEFATP" and defender_client.available:
                device_count = defender_client.device_summary.get('total', 0)
                high_risk = defender_client.device_summary.get('high_risk', 0)
                if device_count > 0:
                    additional_insights.append(f"{device_count} devices, {high_risk} high-risk")
                    if high_risk > 0:
                        base_recommendation = f"Address {high_risk} high-risk devices before Copilot rollout"
            
            elif feature_name.upper() in ["ATP_ENTERPRISE", "EOP_ENTERPRISE_PREMIUM"]:
                alert_count = defender_client.alert_summary.get('total', 0)
                if alert_count > 0:
                    additional_insights.append(f"{alert_count} alerts")
                    base_recommendation = "Review anti-phishing policies for AI-themed threats"
            
            elif feature_name.upper() == "MTP":
                incidents = defender_client.incident_summary.get('total', 0)
                high_severity = defender_client.incident_summary.get('high_severity', 0)
                if incidents > 0:
                    additional_insights.append(f"{incidents} incidents, {high_severity} high-severity")
                    if high_severity > 0:
                        base_recommendation = f"Investigate {high_severity} high-severity incidents"
            
            elif feature_name.upper() in ["ADALLOM_S_O365", "ADALLOM_S_STANDALONE"]:
                oauth_risks = defender_client.oauth_risk_summary.get('high_risk', 0)
                if oauth_risks > 0:
                    additional_insights.append(f"{oauth_risks} high-risk OAuth apps")
                    base_recommendation = f"Review {oauth_risks} high-risk app permissions"
            
            elif feature_name.upper() == "AAD_PREMIUM_IDENTITY_PROTECTION":
                risky_users = defender_client.risky_users_summary.get('total', 0)
                compromised = defender_client.risky_users_summary.get('confirmed_compromised', 0)
                if risky_users > 0:
                    additional_insights.append(f"{risky_users} risky users, {compromised} compromised")
                    if compromised > 0:
                        base_recommendation = f"Revoke access for {compromised} compromised accounts immediately"
        
        # Combine base observation with insights
        if additional_insights:
            base_observation += ". " + ", ".join(additional_insights)
        
        return new_recommendation(
            service="Defender",
            feature=friendly_name,
            observation=base_observation,
            recommendation=base_recommendation,
            link_text="Defender Docs",
            link_url="https://learn.microsoft.com/microsoft-365/security/defender/",
            status=status
        )
    
    # Enhanced recommendations for missing/disabled Defender features
    if status == "PendingActivation":
        obs = f"{friendly_name} is pending activation in {friendly_sku}. M365 Copilot requires comprehensive security protection to safely access organizational data"
        rec = f"Complete activation of {friendly_name} to protect endpoints, emails, and content that M365 Copilot accesses, preventing AI-powered threats and data exposure"
        priority = "High"
    elif status == "Disabled":
        obs = f"{friendly_name} is disabled in {friendly_sku}, leaving M365 Copilot workloads vulnerable to advanced threats and malicious AI usage"
        rec = f"Enable {friendly_name} to provide real-time threat protection, behavioral analysis, and automated response for systems where M365 Copilot processes sensitive organizational knowledge"
        priority = "High"
    else:  # PendingInput, Suspended, Warning, etc.
        obs = f"{friendly_name} has status '{status}' in {friendly_sku}, creating security gaps in M365 Copilot's threat protection"
        rec = f"Resolve the '{status}' status for {friendly_name} to ensure M365 Copilot operates within a secure environment with comprehensive threat detection and prevention"
        priority = "High"  # Security is critical for AI adoption
    
    return new_recommendation(
        service="Defender",
        feature=friendly_name,
        observation=obs,
        recommendation=rec,
        link_text="Microsoft Defender Documentation",
        link_url="https://learn.microsoft.com/microsoft-365/security/defender/",
        priority=priority,
        status=status
    )
