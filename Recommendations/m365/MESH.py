"""
Mesh (Immersive Spaces) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Mesh Immersive Spaces provides 3D environments where AI agents
    can facilitate collaboration in virtual workspaces.
    """
    feature_name = "Mesh (Immersive Spaces)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling immersive 3D collaboration where avatars and agents interact",
            recommendation="",
            link_text="Future of Spatial Collaboration",
            link_url="https://learn.microsoft.com/mesh/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing future immersive collaboration platform",
            recommendation=f"Enable {feature_name} to create persistent 3D workspaces where teams collaborate using avatars with AI assistance. Mesh represents the future of remote collaboration, where AI agents can provide spatial context-aware help, guide users through virtual environments, and facilitate immersive brainstorming sessions. While still emerging, Mesh positions organizations for spatial computing era where Copilot operates in 3D space rather than flat screens. Early adoption enables experimentation with next-generation collaboration paradigms that will become mainstream as VR/AR hardware evolves.",
            link_text="Future of Spatial Collaboration",
            link_url="https://learn.microsoft.com/mesh/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    if status == "Success" and m365_insights and m365_insights.get('available'):
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"3D collaboration readiness: {teams_total_meetings:,} meetings. Mesh (Immersive Spaces) provides 3D virtual workspaces where avatars and AI agents interact spatially. Emerging technology positioning for spatial computing future where Copilot operates in 3D environments, not flat screens.",
            recommendation="",
            link_text="Mesh Platform",
            link_url="https://learn.microsoft.com/mesh/",
            status="Success"
        )
        recommendations.append(obs_rec)
    
    return recommendations
