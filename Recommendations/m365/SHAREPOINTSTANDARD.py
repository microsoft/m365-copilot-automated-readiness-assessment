"""
SharePoint (Plan 2) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    SharePoint Plan 2 provides document management and sites that
    Copilot uses as primary knowledge repository for organization.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "SharePoint (Plan 2)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing the knowledge repository foundation for Copilot",
            recommendation="",
            link_text="SharePoint as Copilot Knowledge Base",
            link_url="https://learn.microsoft.com/sharepoint/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, severely limiting Copilot's access to organizational knowledge",
            recommendation=f"Enable {feature_name} to provide the document library and content management infrastructure that Copilot relies on for organizational knowledge. SharePoint stores team sites, document libraries, lists, and pages that Copilot searches and references when answering questions. Without SharePoint, Copilot cannot access shared organizational content, severely limiting its value beyond personal productivity. Plan 2 includes advanced features like information management policies, enterprise search, and workflow capabilities essential for comprehensive AI-powered knowledge management.",
            link_text="SharePoint as Copilot Knowledge Base",
            link_url="https://learn.microsoft.com/sharepoint/",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # SharePoint activity metrics
        sharepoint_total_sites = m365_insights.get('sharepoint_total_sites', 0)
        sharepoint_active_sites = m365_insights.get('sharepoint_active_sites', 0)
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
        sharepoint_page_views = m365_insights.get('sharepoint_page_views', 0)
        sharepoint_activity_rate = m365_insights.get('sharepoint_activity_rate', 0)
        
        # High SharePoint activity - rich Copilot knowledge base
        if sharepoint_total_sites > 100 and sharepoint_total_files > 10000 and sharepoint_activity_rate > 50:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Rich SharePoint environment with {sharepoint_total_sites} sites, {sharepoint_total_files} files, and {sharepoint_activity_rate:.1f}% activity rate. Copilot has comprehensive knowledge base for organizational queries.",
                recommendation="",
                link_text="SharePoint as Copilot Knowledge Base",
                link_url="https://learn.microsoft.com/sharepoint/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate SharePoint activity - growing knowledge base
        elif sharepoint_total_sites > 20 and sharepoint_total_files > 1000:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate SharePoint usage with {sharepoint_total_sites} sites and {sharepoint_total_files} files ({sharepoint_activity_rate:.1f}% activity). Copilot has foundation knowledge base ready for expansion.",
                recommendation="Encourage teams to migrate legacy file shares and local documents to SharePoint. Each additional site and file enhances Copilot's ability to answer organizational questions and surface relevant content.",
                link_text="SharePoint as Copilot Knowledge Base",
                link_url="https://learn.microsoft.com/sharepoint/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low SharePoint activity - limited Copilot knowledge
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited SharePoint content with {sharepoint_total_sites} sites and {sharepoint_total_files} files. Copilot has minimal organizational knowledge to draw from for contextual assistance.",
                recommendation="Launch SharePoint content migration initiative to build comprehensive knowledge base. Copilot's value multiplies with accessible organizational content - prioritize migrating frequently-referenced documents, templates, and project files to maximize AI-powered knowledge discovery.",
                link_text="SharePoint as Copilot Knowledge Base",
                link_url="https://learn.microsoft.com/sharepoint/",
                priority="High",
                status="Insight"
            )
            recommendations.append(obs_rec)
    
    return recommendations
