"""
Microsoft 365 Copilot in Apps - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    M365 Copilot in Apps embeds AI assistance directly into Word, Excel, PowerPoint,
    Outlook, and other Microsoft 365 applications for in-context productivity.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft 365 Copilot in Apps"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, embedding AI assistance directly into productivity applications",
            recommendation="",
            link_text="Copilot in Microsoft 365 Apps",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-overview",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing AI assistance within productivity applications",
            recommendation=f"Enable {feature_name} to activate Copilot within Word (content generation and editing), Excel (data analysis and formula creation), PowerPoint (presentation design), Outlook (email drafting and summarization), and Teams (meeting summaries and chat assistance). This is the core M365 Copilot experience that transforms how users work in their daily applications, providing contextual AI help exactly where they need it.",
            link_text="Copilot in Microsoft 365 Apps",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-overview",
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
        # ALWAYS create observation showing current Copilot in Apps context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Copilot Apps deployment: {total_active_users:,} users with {email_active_users:,} email users, {sharepoint_total_files:,} files, {teams_total_meetings:,} meetings. Copilot in Apps IS the core M365 Copilot experience - AI embedded in Word, Excel, PowerPoint, Outlook, OneNote. Draft documents, analyze data, design slides, write emails, summarize meetings ALL within familiar apps. This transforms daily productivity workflows with context-aware AI that understands your organization's content and patterns.",
            recommendation="",
            link_text="Maximize Copilot in Apps",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-overview",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # High content volume - maximize Copilot value
        if sharepoint_total_files >= 200 and email_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Rich content foundation: {sharepoint_total_files:,} files and {email_active_users:,} email users create massive Copilot opportunity. Apps can leverage this organizational knowledge.",
                recommendation="Deploy Copilot in Apps training focused on high-value scenarios: Use Word Copilot to draft proposals by referencing existing {sharepoint_total_files:,} files, Excel Copilot to analyze data patterns, Outlook Copilot to manage {email_active_users:,} users' inboxes efficiently, PowerPoint Copilot to create presentations from meeting notes. Measure time savings in document creation and email management.",
                link_text="Deploy Copilot in Apps",
                link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-setup",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)        
        # Moderate adoption potential
        elif total_active_users >= 15 or sharepoint_total_files >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Copilot Apps pilot opportunity: {total_active_users:,} users with {sharepoint_total_files:,} organizational files. Ready for targeted Copilot in Apps deployment.",
                recommendation="Pilot Copilot in Apps with key user groups - document-heavy teams (Word), data analysts (Excel), frequent presenters (PowerPoint), email-intensive roles (Outlook). Track productivity gains, gather feedback, refine prompting techniques before broader rollout.",
                link_text="Pilot Copilot in Apps",
                link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-setup",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    return recommendations
