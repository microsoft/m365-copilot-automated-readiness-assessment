"""
Teams Premium - Management - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Teams Premium Management provides advanced admin controls for governing
    Copilot usage, meeting policies, and agent deployment at scale.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Teams Premium - Management"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing advanced governance for Teams Copilot features",
            recommendation="",
            link_text="Govern Copilot with Teams Premium",
            link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting governance controls for Teams AI features",
            recommendation=f"Enable {feature_name} to control how Copilot operates in Teams meetings and chats. Set policies for AI transcript retention, configure which users can access Copilot meeting summaries, control agent deployment in channels, and enforce meeting templates that optimize Copilot's ability to generate structured outputs. Premium management ensures Copilot adoption aligns with organizational policies while providing admins visibility into AI usage patterns and adoption metrics.",
            link_text="Govern Copilot with Teams Premium",
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
        
        # ALWAYS create observation showing current management context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"AI governance baseline: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users generating Copilot content. Premium Management controls WHO accesses AI summaries, HOW LONG transcripts are retained, WHERE agents can deploy, and WHAT policies govern Copilot usage. Essential for compliance-driven AI adoption - governance must precede scale.",
            recommendation="",
            link_text="AI Governance Controls",
            link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Large Teams deployment - governance critical
        if teams_active_users >= 50 and teams_total_meetings >= 200:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large Teams deployment: {teams_active_users:,} users with {teams_total_meetings:,} meetings. Premium Management critical for governing Copilot at scale.",
                recommendation="Deploy Premium Management controls for Copilot governance. Set policies for meeting transcript retention, control AI summary access, and monitor Copilot usage patterns across organization. Essential for compliance and data protection at scale.",
                link_text="Deploy AI Governance",
                link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate deployment - establish governance
        elif teams_active_users >= 20 or teams_total_meetings >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing Teams usage: {teams_active_users:,} users with {teams_total_meetings:,} meetings. Premium Management enables proactive AI governance.",
                recommendation="Implement Premium Management policies before Copilot expands. Set transcript retention policies and usage controls early to ensure compliance as AI adoption grows.",
                link_text="Establish AI Governance",
                link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
        
    
    return recommendations
