"""
Common Data Service for Office 365 (Plan 2) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for Dynamics integration at scale."""
    try:
        users = await client.users.get()
        return {'available': True, 'user_count': len(users.value) if users and users.value else 0}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Dynamics CDS P2 enables enhanced agent integration.
    Returns 2 recommendations: license status + Dynamics agent scale.
    """
    feature_name = "Common Data Service for Office 365 (Plan 2) - Dynamics"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing enhanced database capacity for agent solutions",
            recommendation="",
            link_text="Enhanced Dataverse for Agents",
            link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing enhanced database platform for complex agents",
            recommendation=f"Enable {feature_name} (Dataverse for Office 365 Plan 2) to provide increased database capacity for agents handling larger datasets and more complex workflows. Plan 2 supports agents that manage substantial business data, maintain extensive conversation histories, and integrate with multiple data sources. Build agents that query customer databases, maintain detailed case histories, or coordinate multi-step approval processes requiring more storage than Plan 1 provides. Essential for production agent scenarios with significant data requirements.",
            link_text="Enhanced Dataverse for Agents",
            link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
            priority="Low",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            user_count = deployment.get('user_count', 0)
            
            # Add capacity data from pp_client
            capacity_info = ""
            if pp_client and hasattr(pp_client, 'capacity_summary'):
                db_usage = pp_client.capacity_summary.get('database_usage_percent', 0)
                capacity_info = f" Database usage: {db_usage:.0f}%."
            
            if user_count > 200:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Enterprise Dynamics Agents",
                    observation=f"Large Dynamics deployment ({user_count} users) ready for production agents.{capacity_info}",
                    recommendation="Scale Dynamics agents for enterprise: 1) Deploy customer service agent across support teams querying D365 case history and knowledge base, 2) Build sales copilot accessing opportunities, leads, contacts for pipeline management, 3) Create field service assistant with work order and scheduling data. Plan 2 capacity supports production agent scale with extensive conversation histories and data access. Monitor Dataverse capacity as agent adoption grows.",
                    link_text="Scale Dynamics Agents",
                    link_url="https://learn.microsoft.com/dynamics365/customer-service/administer/copilot-overview",
                    priority="Medium",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Dynamics Agents",
                    observation="Plan 2 Dataverse ready for Dynamics agent scenarios",
                    recommendation="Build Dynamics agents with enhanced capacity: Query customer records, sales data, service cases for conversational business processes.",
                    link_text="Dynamics Agents",
                    link_url="https://learn.microsoft.com/dynamics365/customer-service/administer/copilot-overview",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Dynamics Planning",
                observation="Enhanced Dataverse for Dynamics available",
                recommendation="Assess Dynamics agent scenarios for customer service, sales, or operations automation.",
                link_text="D365 Agents",
                link_url="https://learn.microsoft.com/dynamics365/customer-service/administer/copilot-overview",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
