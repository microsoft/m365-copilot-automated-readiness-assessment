"""
Microsoft 365 Copilot in SharePoint - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Copilot in SharePoint enables AI-powered content creation, intelligent document
    summarization, and automated site generation from existing organizational knowledge.
    """
    feature_name = "Microsoft 365 Copilot in SharePoint"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing AI assistance for knowledge management and collaboration",
            recommendation="",
            link_text="Copilot in SharePoint Sites",
            link_url="https://learn.microsoft.com/sharepoint/sharepoint-copilot",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting AI capabilities in content repositories",
            recommendation=f"Enable {feature_name} to bring AI assistance to your organization's knowledge base. Create SharePoint sites automatically by describing your needs ('Create a project site for the new product launch'), generate page content from existing documents, get intelligent document summaries, and find related content across your intranet. Copilot in SharePoint makes organizational knowledge more discoverable and actionable, reducing time spent searching for information and ensuring teams can quickly onboard to projects by understanding context from existing materials.",
            link_text="Copilot in SharePoint Sites",
            link_url="https://learn.microsoft.com/sharepoint/sharepoint-copilot",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
        sharepoint_total_sites = m365_insights.get('sharepoint_total_sites', 0)        
        # ALWAYS create observation showing SharePoint Copilot capabilities (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"SharePoint AI readiness: {total_active_users:,} users, {sharepoint_total_files:,} files across {sharepoint_total_sites:,} sites. SharePoint Copilot transforms knowledge management - auto-generate sites from descriptions, create page content from existing docs, summarize multi-document insights, find related content intelligently. Your {sharepoint_total_files:,} files become AI-accessible organizational memory.",
            recommendation="",
            link_text="SharePoint Copilot Features",
            link_url="https://learn.microsoft.com/sharepoint/sharepoint-copilot",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # Rich content repository - SharePoint Copilot high value
        if sharepoint_total_files >= 200 and sharepoint_total_sites >= 5:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Extensive knowledge base: {sharepoint_total_files:,} files across {sharepoint_total_sites:,} sites represent rich organizational memory. SharePoint Copilot high value.",
                recommendation="Deploy SharePoint Copilot training focused on knowledge management scenarios: Use Copilot to create new sites from existing templates, generate page content by referencing your {sharepoint_total_files:,} files, get multi-document summaries (synthesize all Q1 reports), and discover related content across {sharepoint_total_sites:,} sites. Measure time saved in site creation and document research.",
                link_text="SharePoint Copilot Training",
                link_url="https://learn.microsoft.com/sharepoint/sharepoint-copilot",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)        
        # Growing repository - pilot SharePoint AI
        elif sharepoint_total_files >= 50 or sharepoint_total_sites >= 3:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing content: {sharepoint_total_files:,} files across {sharepoint_total_sites:,} sites provide pilot-ready knowledge base.",
                recommendation="Pilot SharePoint Copilot with content-heavy teams: knowledge managers, project leads, department admins. Test site creation ('Create project site for new initiative'), page generation from docs, and document summarization across your {sharepoint_total_files:,} files. Track site creation time and user satisfaction before broader rollout.",
                link_text="Pilot SharePoint Copilot",
                link_url="https://learn.microsoft.com/sharepoint/sharepoint-copilot",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    return recommendations
