"""
People Skills Foundation - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    People Skills Foundation provides skills graph capabilities
    that help Copilot find people with specific expertise.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "People Skills Foundation"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to find experts based on skills and topics",
            recommendation="",
            link_text="Skills-Based Expert Finding",
            link_url="https://learn.microsoft.com/microsoft-365/topics/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting Copilot's ability to connect users with experts",
            recommendation=f"Enable {feature_name} to build a skills graph that Copilot uses to connect people based on expertise and interests. When users ask 'Who knows about Azure architecture?' or 'Find someone experienced with Python', Copilot leverages the skills graph to recommend colleagues. Foundation analyzes documents, emails, and collaboration patterns to infer expertise, making organizational knowledge more discoverable. Enhances Copilot's value for knowledge sharing and team formation by surfacing hidden expertise across the organization.",
            link_text="Skills-Based Expert Finding",
            link_url="https://learn.microsoft.com/microsoft-365/topics/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # ALWAYS create observation showing current skills context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Expertise discovery baseline: {total_active_users:,} users, {sharepoint_total_files:,} SharePoint files, {email_active_users:,} email users. People Skills Foundation builds the expertise graph that Copilot queries - 'Who knows about X?' agents traverse skills, project history, and collaboration patterns to route questions to experts. AI-powered skill matching replaces manual searching, automated expert identification for projects, and knowledge discovery through relationship intelligence.",
            recommendation="",
            link_text="AI Expert Finding",
            link_url="https://learn.microsoft.com/microsoft-365/topics/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Rich content base - strong expertise signals
        if sharepoint_total_files >= 200 and email_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Rich content base: {sharepoint_total_files:,} SharePoint files and {email_active_users:,} email users provide strong expertise signals. Skills graph can accurately identify subject matter experts.",
                recommendation="Leverage People Skills Foundation to surface hidden expertise. With substantial SharePoint content and email collaboration, Copilot can identify experts based on document authorship, email discussions, and collaboration patterns. Train users to ask Copilot 'Who knows about [topic]?' to discover colleagues with relevant expertise.",
                link_text="Discover Organizational Expertise",
                link_url="https://learn.microsoft.com/microsoft-365/topics/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate content - growing expertise graph
        elif sharepoint_total_files >= 50 or email_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing expertise signals: {sharepoint_total_files:,} files and {email_active_users:,} email users. Skills graph is building as content and collaboration increase.",
                recommendation="Encourage SharePoint document creation and Teams collaboration to enrich the skills graph. As users create content and communicate, People Skills Foundation identifies expertise patterns that Copilot uses for expert recommendations.",
                link_text="Build Skills Through Content",
                link_url="https://learn.microsoft.com/microsoft-365/topics/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
