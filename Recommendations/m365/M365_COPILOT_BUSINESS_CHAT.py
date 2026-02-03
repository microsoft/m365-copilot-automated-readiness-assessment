"""
Microsoft 365 Copilot - Business Chat - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Business Chat (copilot.microsoft.com) provides a unified conversational interface
    to interact with all your organizational data across Microsoft 365 and third-party systems.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft 365 Copilot - Business Chat"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling cross-application AI conversations about organizational data",
            recommendation="",
            link_text="Business Chat for Enterprise Search",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-chat",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting unified AI-powered search and synthesis capabilities",
            recommendation=f"Enable {feature_name} to provide employees with a ChatGPT-like experience that works across all their Microsoft 365 data - emails, chats, documents, meetings, and calendar. Business Chat (copilot.microsoft.com) synthesizes information from multiple sources to answer questions like 'What happened in last week's project review?' or 'Summarize all customer feedback from this month.' It's the central hub for AI-powered knowledge work, enabling employees to find answers without knowing where information is stored.",
            link_text="Business Chat for Enterprise Search",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-chat",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)        
        # ALWAYS create observation showing current Business Chat context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Business Chat deployment: {total_active_users:,} users, {email_active_users:,} email users, {sharepoint_total_files:,} files, {teams_total_meetings:,} meetings. Business Chat (copilot.microsoft.com) IS the cross-app Copilot hub - ask questions that span emails, chats, documents, meetings. 'What are this quarter's priorities?' pulls from meetings, emails, SharePoint. The MORE content ({sharepoint_total_files:,} files, {teams_total_meetings:,} meetings), the SMARTER the responses. Central AI interface for knowledge work.",
            recommendation="",
            link_text="Business Chat Best Practices",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-chat",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # Rich organizational knowledge - Business Chat incredibly valuable
        if sharepoint_total_files >= 200 and teams_total_meetings >= 150:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Rich knowledge graph: {sharepoint_total_files:,} files and {teams_total_meetings:,} meetings create massive Business Chat value. Copilot can synthesize across this organizational memory.",
                recommendation="Train users on cross-app Business Chat queries that leverage your {sharepoint_total_files:,} files and {teams_total_meetings:,} meetings. Teach prompts like: 'Summarize decisions from last month's leadership meetings', 'Find all customer feedback about feature X', 'What are the risks mentioned in recent project documents?' Business Chat shines when organizational knowledge is deep - you have the content volume for transformative AI search.",
                link_text="Business Chat Training",
                link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-chat",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)        
        # Moderate content - pilot Business Chat capabilities
        elif sharepoint_total_files >= 50 or teams_total_meetings >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing knowledge base: {sharepoint_total_files:,} files and {teams_total_meetings:,} meetings provide solid Business Chat foundation. Ready for targeted deployment.",
                recommendation="Pilot Business Chat with teams that have rich cross-app workflows - project managers (summarize meetings + docs), sales (customer interactions across email/meetings/files), executives (strategic insights from all sources). As content grows beyond {sharepoint_total_files:,} files, Business Chat becomes more valuable for knowledge discovery.",
                link_text="Pilot Business Chat",
                link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-adoption",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    return recommendations
