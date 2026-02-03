"""
Whiteboard (Plan 3) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Whiteboard provides collaborative canvases where Copilot
    can help organize brainstorming sessions and visualize ideas.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Whiteboard (Plan 3)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-assisted visual collaboration",
            recommendation="",
            link_text="Copilot in Whiteboard",
            link_url="https://learn.microsoft.com/microsoft-365/whiteboard/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing AI-powered brainstorming tools",
            recommendation=f"Enable {feature_name} to let Copilot assist with visual brainstorming and ideation. Use AI to organize sticky notes into themes, generate mind maps from discussion points, suggest related ideas during brainstorming, and create structured frameworks for team collaboration. Whiteboard with Copilot transforms unstructured creative sessions into organized, actionable plans, particularly valuable for hybrid teams collaborating on innovation and strategy.",
            link_text="Copilot in Whiteboard",
            link_url="https://learn.microsoft.com/microsoft-365/whiteboard/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use Teams metrics as proxy for meeting/collaboration culture
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_avg_meetings_per_user = m365_insights.get('teams_avg_meetings_per_user', 0)
        
        
        # High meeting activity - Whiteboard will enhance existing collaboration
        if teams_total_meetings > 1000 and teams_avg_meetings_per_user > 5:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Strong meeting culture detected with {teams_total_meetings} Teams meetings and {teams_avg_meetings_per_user:.1f} average meetings per user. Whiteboard with Copilot will enhance visual brainstorming and idea organization.",
                recommendation="",
                link_text="Copilot in Whiteboard",
                link_url="https://learn.microsoft.com/microsoft-365/whiteboard/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate meeting activity - opportunity for visual collaboration
        elif teams_total_meetings > 300 and teams_avg_meetings_per_user > 2:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate meeting culture with {teams_total_meetings} Teams meetings ({teams_avg_meetings_per_user:.1f} avg per user). Whiteboard with Copilot can structure brainstorming and capture visual ideas.",
                recommendation="Train teams on Whiteboard with Copilot for structured ideation during meetings. Focus on strategy sessions, design thinking workshops, and project planning meetings to maximize visual collaboration ROI.",
                link_text="Copilot in Whiteboard",
                link_url="https://learn.microsoft.com/microsoft-365/whiteboard/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low meeting activity - Whiteboard can establish visual collaboration
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited meeting collaboration with {teams_total_meetings} Teams meetings ({teams_avg_meetings_per_user:.1f} avg per user). Whiteboard with Copilot can establish visual brainstorming culture.",
                recommendation="Launch Whiteboard training program with Copilot-assisted templates for innovation workshops, sprint planning, and retrospectives. Visual collaboration with AI assistance can increase engagement and creativity in hybrid work environments.",
                link_text="Copilot in Whiteboard",
                link_url="https://learn.microsoft.com/microsoft-365/whiteboard/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
