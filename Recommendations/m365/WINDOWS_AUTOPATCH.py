"""
Windows Autopatch - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Windows Autopatch provides automated Windows and M365 app patching
    that ensures devices stay current for Copilot features.
    """
    feature_name = "Windows Autopatch"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, automatically maintaining device currency for Copilot compatibility",
            recommendation="",
            link_text="Automated Patching for AI Readiness",
            link_url="https://learn.microsoft.com/windows/deployment/windows-autopatch/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, requiring manual update management for Copilot features",
            recommendation=f"Enable {feature_name} to automatically patch Windows and M365 apps, ensuring users have the latest Copilot features and compatibility updates. Autopatch eliminates deployment delays for AI capabilities by maintaining current versions across all devices without manual intervention. Reduces help desk burden from version-related Copilot issues, ensures consistent feature availability, and minimizes security risks from outdated systems. Essential for organizations that want Copilot benefits without increased IT overhead for update management.",
            link_text="Automated Patching for AI Readiness",
            link_url="https://learn.microsoft.com/windows/deployment/windows-autopatch/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        
        
        # ALWAYS create observation showing Autopatch automation context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Automated patching: {total_active_users:,} users. Windows Autopatch automatically maintains device currency for Copilot - eliminates manual update deployment, ensures latest AI features available immediately, reduces help desk burden from version issues. Zero-touch update management enabling consistent Copilot experiences without IT overhead.",
            recommendation="",
            link_text="Autopatch Automation",
            link_url="https://learn.microsoft.com/windows/deployment/windows-autopatch/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Larger organizations - Autopatch saves significant IT effort
        if total_active_users >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Organization scale: {total_active_users:,} users indicate significant update management overhead. Autopatch automation valuable.",
                recommendation="Leverage Windows Autopatch to eliminate manual patching effort for {total_active_users:,} devices. Autopatch automatically deploys Windows and M365 updates ensuring Copilot feature parity across organization without IT intervention. Calculate time savings: manual patching requires testing, deployment planning, and rollout coordination - Autopatch handles this automatically. Reduces version fragmentation causing Copilot compatibility issues.",
                link_text="Autopatch Benefits",
                link_url="https://learn.microsoft.com/windows/deployment/windows-autopatch/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(rec)
        
    
    return recommendations
