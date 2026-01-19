"""
Mesh Immersive Spaces for Teams - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Mesh Immersive Spaces provide 3D environments for collaboration
    where AI agents can facilitate virtual interactions.
    """
    feature_name = "Mesh Immersive Spaces for Teams"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-enhanced 3D collaborative environments",
            recommendation="",
            link_text="3D Workspaces with AI Assistants",
            link_url="https://learn.microsoft.com/mesh/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting future immersive collaboration",
            recommendation=f"Enable {feature_name} to create persistent 3D workspaces where teams collaborate using avatars. Immersive Spaces represent the evolution of remote work, where AI agents can act as virtual assistants within 3D environments, guiding new employees through virtual office tours, facilitating spatial brainstorming sessions, and providing contextual help based on user location in the virtual space. While adoption is early, these environments position organizations for the future of spatial computing and ambient AI assistance.",
            link_text="3D Workspaces with AI Assistants",
            link_url="https://learn.microsoft.com/mesh/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        
        # ALWAYS create observation showing 3D collaboration context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Spatial computing readiness: {teams_active_users:,} Teams users, {teams_total_meetings:,} meetings. Mesh Immersive Spaces enable 3D collaboration environments where AI agents provide spatial assistance - virtual office tours, 3D brainstorming, persistent team spaces. Emerging technology positioning for future where Copilot has spatial presence alongside humans in virtual environments.",
            recommendation="",
            link_text="Mesh 3D Collaboration",
            link_url="https://learn.microsoft.com/mesh/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Note: Mesh is emerging technology - no usage-based thresholds as adoption is experimental
        # Focus on awareness rather than deployment scale recommendations
        
    
    return recommendations
