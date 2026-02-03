"""
Common Data Service for Office 365 (Plan 1) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for Dynamics integration opportunities."""
    try:
        users = await client.users.get()
        return {'available': True, 'has_users': users and users.value and len(users.value) > 0}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Dynamics CDS P1 enables agent integration with D365.
    Returns 2 recommendations: license status + Dynamics agent opportunities.
    """
    feature_name = "Common Data Service for Office 365 (Plan 1) - Dynamics"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing database storage for agent conversation history",
            recommendation="",
            link_text="Dataverse for Agents",
            link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing database platform for agent solutions",
            recommendation=f"Enable {feature_name} (Dataverse for Office 365) to provide database storage for custom agents built in Copilot Studio. Plan 1 supports basic agent scenarios that require persistent storage for conversation context, user preferences, and workflow state. Agents store interaction history, remember user preferences across sessions, and maintain state for multi-step processes. Essential for building agents that provide personalized responses based on past interactions and manage stateful workflows rather than simple one-off Q&A.",
            link_text="Dataverse for Agents",
            link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
            priority="Low",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            # Add actual app data from pp_insights
            app_info = ""
            if pp_insights:
                total_apps = pp_insights.get('apps_total', 0)
                if total_apps > 0:
                    app_info = f" You have {total_apps} Power App(s) that could integrate with Dynamics data."
            
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Dynamics Integration",
                observation=f"Dynamics-enabled Dataverse ready for agent integration.{app_info}",
                recommendation="Build Dynamics 365 agents with Copilot Studio: 1) Create customer service agent that queries D365 customer records, order history, and support cases, 2) Build sales assistant that pulls lead/opportunity data, provides pipeline insights, and suggests next actions, 3) Deploy field service agent that accesses work orders, schedules, and equipment data. Connect agents to Dynamics Dataverse tables for real-time business data access. Agents become intelligent interfaces to Dynamics functionality for frontline workers.",
                link_text="Dynamics Agents",
                link_url="https://learn.microsoft.com/dynamics365/customer-service/administer/copilot-overview",
                priority="Medium",
                status="Success"
            )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Dynamics Opportunities",
                observation="Dynamics Dataverse available",
                recommendation="Assess Dynamics agent scenarios: Identify customer service, sales, or field service use cases where agents can simplify access to D365 data.",
                link_text="D365 Agent Scenarios",
                link_url="https://learn.microsoft.com/dynamics365/customer-service/administer/copilot-overview",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
