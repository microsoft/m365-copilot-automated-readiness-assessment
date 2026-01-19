"""
Teams Premium - Customer - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Teams Premium Customer features provide advanced meeting
    customization and branding that enhance agent interactions.
    """
    recommendations = []
    
    feature_name = "Teams Premium - Customer"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling customized meeting experiences for agent-assisted customer interactions",
            recommendation="",
            link_text="Premium Customer Experience Features",
            link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing branded meeting experiences for customer-facing agents",
            recommendation=f"Enable {feature_name} to customize Teams meetings with organization branding, custom backgrounds, and tailored lobbies for external customer meetings where agents participate. Premium customer features enable professional, branded experiences when agents join customer calls, support sessions, or sales meetings. Customize meeting templates that agents use for different customer scenarios, ensuring consistent corporate identity while agents provide AI-powered assistance during customer interactions.",
            link_text="Premium Customer Experience Features",
            link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing/",
            priority="Low",
            status=status
        ))
    
    # M365 Insights - Branded Customer-Facing Agent Experiences
    if m365_insights:
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Teams Premium Customer features provide branded, customized meeting experiences for external customer interactions where Copilot Studio agents participate. Custom lobbies with company branding, tailored backgrounds for customer-facing scenarios, meeting templates optimized for sales/support with agent integration. Professional presentation layer for AI-powered customer service: agents greet customers in branded lobby, provide contextual assistance during meetings, deliver consistent corporate identity across all customer touchpoints. Critical for customer-facing AI deployment maintaining brand standards.",
            recommendation="",
            link_text="Branded Agent Experiences",
            link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing/",
            status="Success"
        ))
        
        # Threshold-based recommendation
        if teams_total_meetings >= 1000:
            recommendations.append(new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"With {teams_total_meetings} Teams meetings, premium customer features ensure professional branded experiences when agents assist in external customer calls",
                recommendation=f"Deploy Teams Premium Customer features for your organization conducting {teams_total_meetings} meetings. Customize meeting templates for customer-facing scenarios where Copilot Studio agents participate - sales calls with AI sales assistants, support sessions with technical agents, consultation meetings with advisory bots. Branded lobbies and backgrounds maintain professional corporate identity while agents provide AI-powered assistance to customers, prospects, and partners.",
                link_text="Customer-Facing AI Deployment",
                link_url="https://learn.microsoft.com/microsoftteams/teams-premium-licensing/",
                status="Insight",
                priority="Medium"
            ))
    
    return recommendations
