"""
Project for Office 365 (Plan 3) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Project for Office 365 provides project management capabilities that
    agents can populate and update based on natural language interactions.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Project for Office 365 (Plan 3)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-assisted project planning and tracking",
            recommendation="",
            link_text="Agent-Driven Project Management",
            link_url="https://learn.microsoft.com/project/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing AI capabilities for project management",
            recommendation=f"Enable {feature_name} to let Copilot assist with project planning and tracking. Use AI to generate project plans from requirements documents, update task statuses based on email and Teams conversations, identify resource conflicts and suggest reallocation, and create status reports automatically. Agents can answer questions about project timelines, critical paths, and resource utilization through natural language queries, making professional project management accessible without extensive PM training.",
            link_text="Agent-Driven Project Management",
            link_url="https://learn.microsoft.com/project/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        sharepoint_total_sites = m365_insights.get('sharepoint_total_sites', 0)
        
        # ALWAYS create observation showing current project context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Project intelligence baseline: {total_active_users:,} users, {teams_total_meetings:,} meetings, {sharepoint_total_sites:,} SharePoint sites. Project for Office 365 becomes AI-powered when combined with Copilot - automated risk identification from meeting transcripts, schedule prediction from historical patterns, resource allocation recommendations, and natural language project queries. Transforms project data into AI-actionable insights.",
            recommendation="",
            link_text="AI Project Management",
            link_url="https://learn.microsoft.com/project/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High project activity indicators - formal PM valuable
        if teams_total_meetings >= 200 and sharepoint_total_sites >= 10:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High project activity: {teams_total_meetings:,} meetings and {sharepoint_total_sites:,} SharePoint sites suggest complex coordination needs. Project with Copilot can centralize project intelligence.",
                recommendation="Deploy Project for Office 365 to centralize project tracking. Use Copilot to auto-generate project plans from Teams discussions, update timelines from email status updates, and create executive summaries from project data.",
                link_text="Copilot Project Automation",
                link_url="https://learn.microsoft.com/project/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate activity - structured PM beneficial
        elif teams_total_meetings >= 50 and total_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate project scale: {total_active_users:,} users with {teams_total_meetings:,} meetings. Project with Copilot can provide structure without PM overhead.",
                recommendation="Introduce Project for key initiatives. Use Copilot to make project management accessible to non-PM roles through natural language queries about timelines, dependencies, and resource allocation.",
                link_text="Accessible Project Management",
                link_url="https://learn.microsoft.com/project/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
