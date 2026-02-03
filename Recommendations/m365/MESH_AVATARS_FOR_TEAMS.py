"""
Mesh Avatars for Teams - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Mesh Avatars provide 3D representations in Teams meetings where
    AI can enhance presence and engagement in immersive environments.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Mesh Avatars for Teams"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, reducing video fatigue by letting participants use 3D avatars while Copilot continues capturing meeting intelligence, speaker identification, and action items",
            recommendation="",
            link_text="Mesh Avatars with Copilot Intelligence",
            link_url="https://learn.microsoft.com/mesh/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing immersive collaboration capabilities",
            recommendation=f"Enable {feature_name} to create personalized avatars for Teams meetings that maintain presence without video fatigue. While still emerging, Mesh environments represent the future of AI-assisted collaboration, where Copilot can provide real-time translation, generate 3D visualizations of concepts being discussed, and create persistent virtual workspaces. Avatars reduce meeting fatigue while maintaining engagement, supporting the hybrid meeting scenarios where Copilot provides meeting summaries and action items.",
            link_text="Immersive Collaboration with Mesh",
            link_url="https://learn.microsoft.com/mesh/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use Teams meeting metrics to assess avatar adoption potential
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_avg_meetings_per_user = m365_insights.get('teams_avg_meetings_per_user', 0)
        
        
        # High meeting volume - avatar adoption can reduce fatigue
        if teams_total_meetings > 1000 and teams_avg_meetings_per_user > 5:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High meeting volume ({teams_total_meetings} meetings, {teams_avg_meetings_per_user:.1f} avg/user) indicates video fatigue risk. Mesh Avatars offer alternative to constant camera-on culture while maintaining engagement.",
                recommendation="",
                link_text="Mesh Avatars with Copilot Intelligence",
                link_url="https://learn.microsoft.com/mesh/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate meeting volume - pilot avatars
        elif teams_total_meetings > 300:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate meeting volume ({teams_total_meetings} meetings). Mesh Avatars can reduce video fatigue while Copilot continues capturing meeting intelligence and action items.",
                recommendation="Pilot Mesh Avatars with teams experiencing meeting fatigue. Focus on long-duration meetings (standups, planning sessions) where camera-off with avatars maintains presence better than profile pictures.",
                link_text="Mesh Avatars with Copilot Intelligence",
                link_url="https://learn.microsoft.com/mesh/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low meeting volume - establish immersive collaboration foundation
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited meeting activity ({teams_total_meetings} meetings). Mesh Avatars represent future of AI-enhanced hybrid collaboration - early adoption prepares organization for Copilot-powered immersive workspaces with avatar intelligence.",
                recommendation="Introduce Mesh Avatars for executive meetings and town halls first. Early adoption establishes immersive collaboration culture while technology matures. Avatars maintain professionalism when video is impractical.",
                link_text="Mesh Avatars with Copilot Intelligence",
                link_url="https://learn.microsoft.com/mesh/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
