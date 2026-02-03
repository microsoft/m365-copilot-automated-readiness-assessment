"""
Microsoft Places (Enhanced) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Places Enhanced uses AI to optimize hybrid work coordination,
    helping teams schedule in-office days when collaboration is most valuable.
    """
    recommendations = []
    
    feature_name = "Microsoft Places (Enhanced)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, using AI to coordinate hybrid work and in-person collaboration",
            recommendation="",
            link_text="AI-Powered Workspace Coordination",
            link_url="https://learn.microsoft.com/microsoft-365/places/overview",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing intelligent hybrid work coordination",
            recommendation=f"Enable {feature_name} to use AI for coordinating when distributed teams come together. While Copilot handles remote collaboration, Places ensures teams align office presence for high-value activities like brainstorming, relationship building, and complex problem-solving that benefit from in-person interaction. Places analyzes calendars and work patterns to suggest optimal collaboration days, complementing Copilot's virtual assistance with strategic physical presence.",
            link_text="AI-Powered Workspace Coordination",
            link_url="https://learn.microsoft.com/microsoft-365/places/overview",
            priority="Low",
            status=status
        ))
    
    # M365 Insights - AI-Powered Hybrid Work Optimization
    if m365_insights:
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Places Enhanced uses AI to analyze calendar patterns, team collaboration needs, office capacity to suggest optimal in-person days. Advanced features: predictive analytics for space planning, automated desk/room suggestions based on meeting attendees, AI-driven recommendations for which work requires physical presence. Complements Copilot remote collaboration with intelligent physical workspace coordination. Premium tier for organizations balancing remote AI tools with strategic in-office collaboration.",
            recommendation="",
            link_text="AI Hybrid Work Analytics",
            link_url="https://learn.microsoft.com/microsoft-365/places/overview",
            status="Success"
        ))
        
        # Threshold-based recommendation
        if teams_active_users >= 50:
            recommendations.append(new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"With {teams_active_users} Teams users in hybrid work, Places Enhanced can optimize when teams come together for high-value collaboration",
                recommendation=f"Deploy Places Enhanced AI features for your {teams_active_users} hybrid Teams users. Enable predictive space planning, automated collaboration day recommendations, AI-driven desk assignments based on meeting patterns. Ensures teams align office presence for activities that benefit from in-person interaction (brainstorming, relationship building) while Copilot handles remote collaboration.",
                link_text="Enhanced Hybrid Coordination",
                link_url="https://learn.microsoft.com/microsoft-365/places/overview",
                status="Insight",
                priority="Low"
            ))
    
    return recommendations
