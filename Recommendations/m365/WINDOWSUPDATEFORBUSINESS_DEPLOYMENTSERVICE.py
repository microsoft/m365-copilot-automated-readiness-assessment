"""
Windows Update for Business Deployment Service - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Windows Update for Business provides update management that
    ensures devices stay current for Copilot compatibility.
    """
    feature_name = "Windows Update for Business"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, ensuring Windows devices stay current for Copilot features",
            recommendation="",
            link_text="Manage Updates for Copilot Readiness",
            link_url="https://learn.microsoft.com/windows/deployment/update/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, risking outdated Windows versions for Copilot",
            recommendation=f"Enable {feature_name} to ensure Windows devices receive timely updates required for Windows Copilot and other AI features. Automated update deployment keeps devices current with security patches and feature releases, minimizing compatibility issues with M365 Copilot integrations. Properly managed updates ensure users can access the latest AI capabilities as they're released, maintaining consistent Copilot experiences across the organization.",
            link_text="Manage Updates for Copilot Readiness",
            link_url="https://learn.microsoft.com/windows/deployment/update/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        
        
        # ALWAYS create observation showing Windows update management context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Device update management: {total_active_users:,} users. Windows Update for Business ensures devices stay current for Copilot compatibility - automated deployment of security patches and feature releases. Minimizes version fragmentation that causes Copilot integration issues. Device management foundation enabling consistent AI capabilities across organization.",
            recommendation="",
            link_text="Update Management",
            link_url="https://learn.microsoft.com/windows/deployment/update/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Note: Windows Update for Business is infrastructure/device management - no usage-based thresholds
        # Critical for any organization deploying Copilot, regardless of user count
        # Focus on awareness rather than scale-based recommendations
        
    
    return recommendations
