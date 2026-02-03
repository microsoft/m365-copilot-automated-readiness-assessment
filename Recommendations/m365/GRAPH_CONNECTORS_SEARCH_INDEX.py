"""
Graph Connectors Search Index - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Graph Connectors Search Index enables indexing of external
    content sources that Copilot can search and reference.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Graph Connectors Search Index"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to access external data sources via Graph Connectors",
            recommendation="",
            link_text="Extend Copilot to External Data",
            link_url="https://learn.microsoft.com/graph/connecting-external-content-connectors-overview/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting Copilot to M365-native content only",
            recommendation=f"Enable {feature_name} to index external content sources (ServiceNow, Salesforce, file shares, databases) that Copilot can search and include in responses. Graph Connectors dramatically expand Copilot's knowledge beyond M365 by ingesting third-party system data into Microsoft Search. Users can ask 'What's the status of ticket #12345 in ServiceNow?' and receive answers grounded in external systems. Critical for organizations with knowledge distributed across multiple platforms, enabling unified AI-powered search across the entire digital workplace.",
            link_text="Extend Copilot to External Data",
            link_url="https://learn.microsoft.com/graph/connecting-external-content-connectors-overview/",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
        sharepoint_total_sites = m365_insights.get('sharepoint_total_sites', 0)
        total_active_users = m365_insights.get('total_active_users', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        
        # ALWAYS create observation showing current search index context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Knowledge integration baseline: {sharepoint_total_files:,} SharePoint files across {sharepoint_total_sites:,} sites for {total_active_users:,} users. Graph Connectors EXPAND Copilot's knowledge beyond M365 - index Salesforce, ServiceNow, SAP, custom databases into Microsoft Graph so agents query ALL organizational knowledge, not just Office files. Without connectors, Copilot operates with partial visibility. Critical for enterprise AI that needs complete context.",
            recommendation="",
            link_text="External Knowledge Integration",
            link_url="https://learn.microsoft.com/graph/connecting-external-content-connectors-overview/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Substantial M365 content - ready for external connectors
        if sharepoint_total_files >= 200 and total_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Rich M365 content base: {sharepoint_total_files:,} files for {total_active_users:,} users. Organization ready for Graph Connectors to integrate external knowledge sources.",
                recommendation="Deploy Graph Connectors to expand Copilot knowledge beyond M365. Prioritize high-value systems: ServiceNow tickets, Salesforce customer data, Jira issues, network file shares. This enables comprehensive AI responses spanning internal and external data.",
                link_text="Deploy Knowledge Connectors",
                link_url="https://learn.microsoft.com/graph/connecting-external-content-connectors-overview/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Growing content - consider connectors
        elif sharepoint_total_files >= 50 or total_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate content base: {sharepoint_total_files:,} SharePoint files for {total_active_users:,} users. Consider Graph Connectors to enrich Copilot's knowledge base.",
                recommendation="Plan Graph Connector deployment for critical external systems. Start with one high-value connector (e.g., support ticketing system) to demonstrate unified search before scaling to additional sources.",
                link_text="Plan Connector Strategy",
                link_url="https://learn.microsoft.com/graph/connecting-external-content-connectors-overview/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
