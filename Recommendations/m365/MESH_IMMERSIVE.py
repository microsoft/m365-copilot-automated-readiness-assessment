"""
Mesh (Immersive Spaces) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Mesh Immersive Spaces provide 3D collaboration environments
    where avatars and agents can interact in virtual settings.
    """
    feature_name = "Mesh Immersive Spaces (Standalone)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling spatial computing environments where Copilot and AI agents can provide immersive assistance in 3D collaboration spaces",
            recommendation="",
            link_text="Mesh for Spatial AI Collaboration",
            link_url="https://learn.microsoft.com/mesh/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing immersive collaboration capabilities",
            recommendation=f"Enable {feature_name} to create 3D virtual environments for team collaboration where avatars represent participants and AI agents can provide assistance. Build immersive training sessions where agents guide employees through procedures in virtual spaces, conduct virtual town halls where AI assistants answer questions from avatar-represented attendees, or create persistent team spaces where agents maintain presence. Mesh integration with Teams enables natural transition between traditional meetings and immersive experiences, with Copilot potentially summarizing both types of interactions. Represents next evolution of hybrid work where AI assistants have spatial presence alongside human participants.",
            link_text="3D Collaboration Spaces",
            link_url="https://learn.microsoft.com/mesh/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        
        # ALWAYS create observation showing standalone Mesh context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"3D environment foundation: {teams_active_users:,} Teams users, {teams_total_meetings:,} meetings. Mesh Immersive (Standalone) creates persistent 3D virtual environments where AI agents have spatial presence - training simulations with agent guides, virtual town halls with AI assistants, team spaces with ambient agent support. Future of work where Copilot operates in 3D alongside humans, not just chat interfaces.",
            recommendation="",
            link_text="Standalone Mesh Environments",
            link_url="https://learn.microsoft.com/mesh/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Note: Standalone Mesh is advanced/experimental - no usage thresholds as this is future-looking technology
        # Organizations adopt for specific scenarios (training, events) not broad rollout
        
    
    return recommendations
