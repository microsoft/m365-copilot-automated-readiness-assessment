"""
Graph Connectors for Copilot - M365 Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name
from azure.core.exceptions import HttpResponseError

async def get_deployment_status(client):
    """
    Check actual deployed Graph Connectors via Microsoft Graph API.
    
    API: GET /external/connections
    Permission: ExternalConnection.Read.All
    Docs: https://learn.microsoft.com/graph/api/externalconnectors-external-list-connections
    
    Args:
        client: Microsoft Graph client
        
    Returns:
        dict with deployment information or None if check fails
    """
    try:
        connections = await client.external.connections.get()
        
        connectors = []
        if connections and connections.value:
            for conn in connections.value:
                connectors.append({
                    'id': conn.id,
                    'name': conn.name or conn.id,
                    'state': conn.state if hasattr(conn, 'state') else 'unknown',
                    'description': conn.description if hasattr(conn, 'description') else ''
                })
        
        return {
            'available': True,
            'connectors': connectors,
            'total_connectors': len(connectors)
        }
    except HttpResponseError as e:
        if e.status_code == 401:
            return {'available': False, 'reason': 'Authentication failed (requires ExternalConnection.Read.All permission)'}
        if e.status_code == 403:
            return {'available': False, 'reason': 'Permission denied (requires ExternalConnection.Read.All permission)'}
        return {'available': False, 'reason': f'API error {e.status_code}'}
    except Exception as e:
        # Simplified error message - just the error type
        error_type = type(e).__name__
        return {'available': False, 'reason': f'{error_type}: Insufficient permissions'}

async def get_recommendation(sku_name, status="Success", client=None, m365_insights=None):
    """
    Graph Connectors enable Copilot to access and reason over external data sources,
    making third-party content searchable and actionable through AI.
    
    Returns 2-3 recommendations:
    1. License status (active/inactive)
    2. Deployment status (connectors deployed, data sources connected)
    3. Usage context (if m365_insights available) - NEW
    
    Args:
        sku_name: SKU name where feature is found
        status: Provisioning status
        client: Optional Graph client for deployment check
        m365_insights: Optional M365 usage metrics
    
    Returns:
        list: Recommendation dicts
    """
    feature_name = "Graph Connectors for Copilot"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # RECOMMENDATION 1: License Status (EXISTING - unchanged)
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to access external knowledge sources",
            recommendation="",
            link_text="Graph Connectors Documentation",
            link_url="https://learn.microsoft.com/graph/connecting-external-content-connectors-overview",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting Copilot to only Microsoft 365 content",
            recommendation=f"Enable {feature_name} to connect M365 Copilot to external data sources like ServiceNow, Salesforce, Jira, custom databases, and file shares. Graph Connectors index external content into Microsoft Graph, making it searchable and actionable through Copilot. Without this, Copilot can only access content in SharePoint, OneDrive, and Teams - missing critical business data stored in third-party systems.",
            link_text="Enable Graph Connectors",
            link_url="https://learn.microsoft.com/graph/connecting-external-content-connectors-overview",
            priority="High",
            status=status
        ))
    
    # RECOMMENDATION 2: Deployment Check (only if license is active)
    if status == "Success":
        deployment_data = None
        if client:
            deployment_data = await get_deployment_status(client)
        
        if deployment_data and deployment_data.get('available'):
            connector_count = deployment_data.get('total_connectors', 0)
            
            if connector_count > 0:
                # GOOD: Connectors deployed
                connector_names = [c['name'] for c in deployment_data.get('connectors', [])[:3]]
                connectors_summary = ', '.join(connector_names)
                if connector_count > 3:
                    connectors_summary += f" (and {connector_count - 3} more)"
                
                recommendations.append(new_recommendation(
                    service="M365",
                    feature="Graph Connectors Deployment",
                    observation=f"{connector_count} Graph Connector(s) deployed and indexing data: {connectors_summary}",
                    recommendation="",
                    link_text="Manage Connectors",
                    link_url="https://admin.microsoft.com/Adminportal/Home#/MicrosoftSearch/connectors",
                    status="Success"
                ))
            else:
                # CRITICAL GAP: Zero connectors deployed
                recommendations.append(new_recommendation(
                    service="M365",
                    feature="Graph Connectors Deployment",
                    observation=f"ZERO Graph Connectors deployed - Copilot cannot access any external data sources",
                    recommendation=f"URGENT: Deploy Graph Connectors to unlock Copilot's full potential. Without connectors, Copilot is limited to Microsoft 365 content only (SharePoint, OneDrive, Teams). Deploy connectors for critical systems like ServiceNow, Salesforce, Jira, custom databases, and file shares. This is a major gap preventing comprehensive AI assistance. Start with high-impact data sources where employees frequently search for information.",
                    link_text="Deploy Connectors Now",
                    link_url="https://learn.microsoft.com/graph/connecting-external-content-connectors-overview",
                    priority="High",
                    status="Warning"
                ))
        elif deployment_data and not deployment_data.get('available'):
            # Could not verify - show actionable guidance instead of technical error
            recommendations.append(new_recommendation(
                service="M365",
                feature="Graph Connectors Deployment",
                observation=f"Graph Connectors license is active in {friendly_sku}. Deployment status requires manual verification.",
                recommendation=f"Check Graph Connectors deployment status to ensure Copilot can access external data sources. Graph Connectors extend Copilot beyond Microsoft 365 content to include ServiceNow, Salesforce, Jira, databases, and file shares. Without deployed connectors, Copilot is limited to SharePoint, OneDrive, and Teams content only. Verify connectors are deployed and indexing data from your critical business systems.",
                link_text="Verify Graph Connectors Deployment",
                link_url="https://admin.microsoft.com/Adminportal/Home#/MicrosoftSearch/connectors",
                priority="Medium",
                status="PendingInput"
            ))
        else:
            # No client provided - show actionable guidance
            recommendations.append(new_recommendation(
                service="M365",
                feature="Graph Connectors Deployment",
                observation=f"Graph Connectors license is active in {friendly_sku}. Deployment status requires manual verification.",
                recommendation=f"Check Graph Connectors deployment to maximize Copilot's value. Graph Connectors enable Copilot to search and reason over external data from ServiceNow, Salesforce, Jira, custom databases, and file shares. Without connectors, Copilot only accesses Microsoft 365 content (SharePoint, OneDrive, Teams). Deploy connectors for critical business systems to provide comprehensive AI assistance across your entire data ecosystem.",
                link_text="Verify Graph Connectors Deployment",
                link_url="https://admin.microsoft.com/Adminportal/Home#/MicrosoftSearch/connectors",
                priority="Medium",
                status="PendingInput"
            ))
    
    # RECOMMENDATION 3: Usage Context (NEW - based on m365_insights)
    if status == "Success" and m365_insights and m365_insights.get('sharepoint_report_available'):
        total_sites = m365_insights.get('total_sites', 0)
        
        if total_sites > 50:
            # High site count = strong case for external data integration
            recommendations.append(new_recommendation(
                service="M365",
                feature="Graph Connectors for Copilot",
                observation=f"Your tenant has {total_sites} SharePoint sites. This significant content base creates strong opportunities for Graph Connectors to integrate external data sources, enabling Copilot to provide unified answers across Microsoft 365 and third-party systems.",
                recommendation="",  # No recommendation - this is helpful context
                link_text="",
                link_url="",
                priority="",
                status=""
            ))
        elif total_sites >= 10:
            # Moderate site count = suggest connectors for key systems
            recommendations.append(new_recommendation(
                service="M365",
                feature="Graph Connectors for Copilot",
                observation=f"Your tenant has {total_sites} SharePoint sites. Consider deploying Graph Connectors to integrate external data from ServiceNow, Salesforce, or custom databases, expanding Copilot's knowledge base beyond Microsoft 365.",
                recommendation=f"Evaluate Graph Connectors for key external systems. With {total_sites} SharePoint sites, your users already have substantial Microsoft 365 content. Adding external data sources through Graph Connectors will enable Copilot to provide comprehensive answers that span both Microsoft 365 and third-party platforms, improving productivity and decision-making.",
                link_text="Explore Graph Connectors",
                link_url="https://learn.microsoft.com/microsoft-365-copilot/extensibility/overview-graph-connector",
                priority="Low",
                status="PendingInput"
            ))
        else:
            # Low site count = focus on M365 content first
            recommendations.append(new_recommendation(
                service="M365",
                feature="Graph Connectors for Copilot",
                observation=f"Your tenant has {total_sites} SharePoint sites. Focus on building Microsoft 365 content (SharePoint, Teams, OneDrive) before investing in Graph Connectors for external data.",
                recommendation=f"Build Microsoft 365 content foundation before deploying Graph Connectors. With only {total_sites} SharePoint sites, prioritize creating and organizing content in SharePoint, Teams, and OneDrive first. Once your Microsoft 365 content base is established, then add external data sources through Graph Connectors to maximize Copilot's value.",
                link_text="SharePoint Content Planning",
                link_url="https://learn.microsoft.com/sharepoint/plan-site-architecture",
                priority="Medium",
                status="PendingInput"
            ))

    return recommendations
