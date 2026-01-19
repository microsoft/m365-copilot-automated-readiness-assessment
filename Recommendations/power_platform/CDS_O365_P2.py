"""
Common Data Service for Office 365 (Plan 2) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for capacity needs."""
    try:
        users = await client.users.get()
        return {'available': True, 'user_count': len(users.value) if users and users.value else 0}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    CDS P2 provides enhanced Dataverse for agents.
    Returns 2 recommendations: license status + upgrade path.
    """
    feature_name = "Common Data Service for Office 365 (Plan 2)"
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
            
            # Add actual capacity data from pp_client
            capacity_info = ""
            if pp_client and hasattr(pp_client, 'capacity_summary'):
                db_usage = pp_client.capacity_summary.get('database_usage_percent', 0)
                capacity_info = f" Current usage: {db_usage:.0f}% of Plan 2 capacity."
            
            if user_count > 1000:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Enterprise Capacity",
                    observation=f"Enterprise organization ({user_count} users) may need premium Dataverse capacity.{capacity_info}",
                    recommendation="Consider Plan 3 for enterprise agent scenarios: Plan 2 provides enhanced capacity suitable for production agents. For enterprise scale (1000+ users) with AI Builder needs, advanced analytics, or premium capacity requirements, evaluate Plan 3 upgrade. Monitor usage patterns in Power Platform admin center to identify when Plan 2 capacity becomes constraining.",
                    link_text="Premium Capacity Planning",
                    link_url="https://learn.microsoft.com/power-platform/admin/capacity-storage",
                    priority="Low",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Enhanced Storage",
                    observation="Plan 2 Dataverse provides enhanced capacity for production agents",
                    recommendation="Use Plan 2 for production agent deployments: Suitable for most agent scenarios with enhanced storage. If AI Builder or premium features needed, consider Plan 3 upgrade path.",
                    link_text="Dataverse Capacity",
                    link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Capacity",
                observation="Enhanced Dataverse capacity available",
                recommendation="Monitor agent data storage and plan capacity management as usage grows.",
                link_text="Capacity Management",
                link_url="https://learn.microsoft.com/power-platform/admin/capacity-storage",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
