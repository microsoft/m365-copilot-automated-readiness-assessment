"""
Teams Premium - Customer - M365 & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Teams Premium - Customer provides enhanced customer engagement capabilities.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Teams Premium - Customer"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-powered customer engagement and queue management for agent-assisted support",
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
            recommendation=f"Enable {feature_name} to provide advanced customer engagement features in Teams.",
            link_text="Teams Premium Overview",
            link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        # ALWAYS create observation showing current customer context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Customer engagement baseline: {teams_total_meetings:,} Teams meetings with {teams_active_users:,} active users. Premium Customer features enable AI-powered queue management with intelligent routing, automated customer history retrieval for agents via Copilot, and AI-generated meeting summaries for support interactions. Scales personalized service through AI augmentation.",
            recommendation="",
            link_text="AI Customer Engagement",
            link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High customer interaction - premium features valuable
        if teams_total_meetings >= 150 and teams_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High customer interaction volume: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users. Premium Customer features can enhance support operations.",
                recommendation="Deploy Premium Customer features for customer-facing teams. Enable AI-powered queue management, automated customer routing, and intelligent meeting summaries for support interactions. Scales personalized customer service with AI.",
                link_text="Deploy Customer Features",
                link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate activity - pilot customer features
        elif teams_total_meetings >= 50 or teams_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing customer engagement: {teams_total_meetings:,} meetings with {teams_active_users:,} users. Premium Customer features can improve service quality.",
                recommendation="Pilot Premium Customer features with support or sales team. Test AI queue management and meeting intelligence before expanding to all customer-facing roles.",
                link_text="Start Customer Features",
                link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
        
    
    return recommendations
