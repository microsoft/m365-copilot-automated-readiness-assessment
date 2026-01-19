"""
Viva Insights (Backend) - M365 & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Viva Insights (Backend) provides work pattern analytics backend services.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Viva Insights (Backend)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in Microsoft 365 Copilot, providing analytics infrastructure for measuring Copilot impact",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to provide work pattern analytics backend services for Viva Insights. Essential infrastructure for measuring organizational productivity improvements from Copilot adoption.",
            link_text="Viva Insights Overview",
            link_url="https://learn.microsoft.com/viva/insights/introduction",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations - Analytics backend context
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        

        # ALWAYS create observation showing current metrics (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Analytics backend active for {total_active_users:,} users with {teams_total_meetings:,} meetings. Viva Insights Backend processes collaboration data to track Copilot's measurable impact on meeting reduction and productivity gains across your organization.",
            recommendation="",
            link_text="Viva Insights Analytics",
            link_url="https://learn.microsoft.com/viva/insights/",
            status="Success"
        )
        recommendations.append(obs_rec)
    
    return recommendations
