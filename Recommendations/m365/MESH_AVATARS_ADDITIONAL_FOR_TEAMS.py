"""
Mesh Avatars for Teams (Additional) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Mesh Avatars Additional provides extended avatar customization and
    enhanced immersive meeting experiences in Teams with AI assistance.
    """
    feature_name = "Mesh Avatars for Teams (Additional)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling extended avatar customization for AI-enhanced meetings",
            recommendation="",
            link_text="Enhanced Mesh Avatar Experiences",
            link_url="https://learn.microsoft.com/mesh/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting advanced avatar customization",
            recommendation=f"Enable {feature_name} to provide additional avatar customization options and enhanced immersive experiences in Teams meetings. While Mesh avatars reduce video fatigue and maintain engagement, the additional features enable more personalized representations in hybrid meetings where Copilot provides real-time summaries and action items. As AI-assisted collaboration evolves, these immersive environments will support spatial computing scenarios where Copilot can visualize complex concepts in 3D and create persistent virtual workspaces.",
            link_text="Enhanced Mesh Avatar Experiences",
            link_url="https://learn.microsoft.com/mesh/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        
        # ALWAYS create observation showing Mesh avatar context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Immersive meeting readiness: {teams_active_users:,} Teams users, {teams_total_meetings:,} meetings. Mesh Avatars (Additional) provide extended customization for video-off meetings - combat Zoom fatigue while maintaining engagement. AI-enhanced avatars with gesture recognition and spatial audio. Early-stage technology preparing for future where Copilot operates in 3D spatial environments, not just 2D screens.",
            recommendation="",
            link_text="Mesh Avatar Features",
            link_url="https://learn.microsoft.com/mesh/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High meeting volume - avatar features could reduce fatigue
        if teams_total_meetings >= 100:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Heavy meeting load: {teams_total_meetings:,} meetings suggest video fatigue risk. Avatar-based meetings offer alternative.",
                recommendation="Pilot Mesh avatars with meeting-heavy teams experiencing video fatigue. With {teams_total_meetings:,} meetings, users report exhaustion from constant on-camera presence. Avatars maintain engagement without video burden, particularly for internal collaboration. Test with teams doing daily standups or long working sessions. Early adoption positions organization for spatial computing future where Copilot assists in 3D environments.",
                link_text="Mesh Avatar Pilot",
                link_url="https://learn.microsoft.com/mesh/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(rec)
        
    
    return recommendations
