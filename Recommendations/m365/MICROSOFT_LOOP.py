"""
Microsoft Loop - M365 Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Loop enables collaborative canvases where teams work together with
    Copilot to brainstorm, plan, and create content in real-time.
    
    Args:
        sku_name: SKU name
        status: Provisioning status  
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft Loop"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling collaborative AI-assisted workspace creation",
            recommendation="",
            link_text="Collaborate with Copilot in Loop",
            link_url="https://learn.microsoft.com/microsoft-loop/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing modern collaborative workspace for AI-assisted teamwork",
            recommendation=f"Enable {feature_name} to provide flexible, AI-powered collaborative workspaces. Loop integrates deeply with Copilot, allowing teams to brainstorm ideas, generate content, and iterate on projects together in real-time with AI assistance. Loop components sync across Microsoft 365, so Copilot-generated content in Loop automatically updates in Teams, Outlook, and other apps. Loop represents the future of collaborative work where teams and AI co-create seamlessly.",
            link_text="Collaborate with Copilot in Loop",
            link_url="https://learn.microsoft.com/microsoft-loop/",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use SharePoint and Teams metrics as proxy for collaboration potential
        sharepoint_total_sites = m365_insights.get('sharepoint_total_sites', 0)
        sharepoint_active_sites = m365_insights.get('sharepoint_active_sites', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # High collaboration activity - Loop will augment existing workflows
        if sharepoint_total_sites > 50 and teams_total_meetings > 500:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Organization has strong collaboration foundation with {sharepoint_total_sites} SharePoint sites and {teams_total_meetings} Teams meetings. Microsoft Loop will enhance collaborative content creation with Copilot integration.",
                recommendation="",
                link_text="Collaborate with Copilot in Loop",
                link_url="https://learn.microsoft.com/microsoft-loop/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate collaboration activity - opportunity for Loop adoption
        elif sharepoint_total_sites > 20 and teams_total_meetings > 200:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Organization has {sharepoint_total_sites} SharePoint sites and {teams_total_meetings} Teams meetings, indicating moderate collaboration. Microsoft Loop with Copilot can consolidate workflows.",
                recommendation="Pilot Microsoft Loop in key teams to enable real-time collaborative canvases with Copilot assistance for brainstorming and planning.",
                link_text="Collaborate with Copilot in Loop",
                link_url="https://learn.microsoft.com/microsoft-loop/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low collaboration activity - Loop can jumpstart culture shift
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited collaboration detected with {sharepoint_total_sites} SharePoint sites and {teams_total_meetings} Teams meetings. Microsoft Loop with Copilot can transform team collaboration patterns.",
                recommendation="Launch Microsoft Loop training program to establish collaborative work culture with Copilot-powered canvases for ideation and project planning.",
                link_text="Collaborate with Copilot in Loop",
                link_url="https://learn.microsoft.com/microsoft-loop/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
