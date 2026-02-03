"""
Common Data Service for Office 365 (Plan 1) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for capacity needs."""
    try:
        users = await client.users.get()
        return {'available': True, 'user_count': len(users.value) if users and users.value else 0}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    CDS P1 provides basic Dataverse for agents.
    Returns 2 recommendations: license status + upgrade path.
    """
    feature_name = "Common Data Service for Office 365 (Plan 1)"
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
            user_count = deployment.get('user_count', 0)
            
            # Add actual capacity data from pp_client
            capacity_info = ""
            if pp_client and hasattr(pp_client, 'capacity_summary'):
                db_usage = pp_client.capacity_summary.get('database_usage_percent', 0)
                capacity_info = f" Current usage: {db_usage:.0f}% of allocated capacity."
            
            if user_count > 500:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Capacity Planning",
                    observation=f"Large organization ({user_count} users) may need enhanced Dataverse capacity.{capacity_info}",
                    recommendation="Consider upgrading to Plan 2 or Plan 3 for increased Dataverse capacity: Plan 1 provides basic storage suitable for simple agents with limited data. As agent adoption grows, you may need Plan 2 (enhanced capacity) or Plan 3 (premium capacity + advanced features). Monitor Dataverse storage usage in Power Platform admin center - upgrade when nearing capacity limits or needing advanced features like AI Builder.",
                    link_text="Dataverse Capacity Planning",
                    link_url="https://learn.microsoft.com/power-platform/admin/capacity-storage",
                    priority="Low",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Basic Storage",
                    observation="Plan 1 Dataverse available for basic agent storage",
                    recommendation="Use Plan 1 for basic agent data: Suitable for agents with simple conversation storage needs. If you need AI Builder, advanced analytics, or significantly more capacity, plan upgrade path to Plan 3.",
                    link_text="Dataverse Plans",
                    link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Storage",
                observation="Basic Dataverse capacity available",
                recommendation="Assess storage needs for agent data and plan capacity upgrades as adoption grows.",
                link_text="Dataverse Storage",
                link_url="https://learn.microsoft.com/power-platform/admin/capacity-storage",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
