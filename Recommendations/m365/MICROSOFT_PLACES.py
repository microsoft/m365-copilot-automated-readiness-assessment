"""
Microsoft Places (Core) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Places provides workplace coordination features
    that help employees and agents manage hybrid work schedules.
    """
    feature_name = "Microsoft Places (Core)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling workplace coordination that agents can query and manage",
            recommendation="",
            link_text="Hybrid Workplace Coordination",
            link_url="https://learn.microsoft.com/microsoft-365/places/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing workplace coordination capabilities for agent-assisted hybrid work",
            recommendation=f"Enable {feature_name} to coordinate office presence, desk booking, and meeting room scheduling that M365 Copilot and custom agents can access. Places helps employees see when teammates will be in office, find nearby colleagues, and book workspaces. Build agents that answer 'who's in the office tomorrow?', coordinate team in-person days, or suggest optimal meeting times based on office presence. Copilot uses Places data to provide contextual recommendations about where to work and when to collaborate in-person, optimizing hybrid work patterns through AI-driven insights.",
            link_text="Hybrid Workplace Coordination",
            link_url="https://learn.microsoft.com/microsoft-365/places/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    if status == "Success" and m365_insights and m365_insights.get('available'):
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Hybrid work coordination: {teams_active_users:,} Teams users. Microsoft Places coordinates office presence, desk booking, room scheduling - agents can query 'who's in office tomorrow?', coordinate in-person days. Copilot uses Places data for hybrid work optimization - suggest meeting times based on office presence patterns.",
            recommendation="",
            link_text="Places Features",
            link_url="https://learn.microsoft.com/microsoft-365/places/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        if teams_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Hybrid workforce: {teams_active_users:,} Teams users likely need office coordination for effective in-person collaboration.",
                recommendation="Deploy Places for hybrid work coordination with your {teams_active_users:,} Teams users. Enable agents that answer presence questions, coordinate team office days, and suggest optimal in-person meeting times. Monitor office utilization patterns to optimize space and facilitate spontaneous collaboration.",
                link_text="Places Deployment",
                link_url="https://learn.microsoft.com/microsoft-365/places/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
