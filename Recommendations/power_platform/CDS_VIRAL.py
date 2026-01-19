"""
Common Data Service (Viral) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check if trial environment suitable for PoC."""
    try:
        users = await client.users.get()
        return {'available': True, 'has_users': users and users.value and len(users.value) > 0}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    CDS Viral provides trial data storage for agents.
    Returns 2 recommendations: license status + trial optimization.
    """
    feature_name = "Common Data Service (Viral)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing limited data storage for agent prototypes and trials",
            recommendation="",
            link_text="Trial Data Platform for Agents",
            link_url="https://learn.microsoft.com/power-platform/admin/powerapps-flow-licensing-faq#common-data-service/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting ability to trial agent solutions",
            recommendation=f"Enable {feature_name} to provide free trial capacity in Dataverse for experimenting with agent solutions and Power Platform workflows. Viral CDS allows users to create proof-of-concept agents, test conversation flows, and prototype automation without procurement delays. While limited in capacity and features compared to licensed CDS, it enables rapid experimentation with agent scenarios before committing to full licenses. Useful for citizen developers exploring agent capabilities and IT evaluating Copilot Studio's potential before enterprise deployment.",
            link_text="Trial Data Platform for Agents",
            link_url="https://learn.microsoft.com/power-platform/admin/powerapps-flow-licensing-faq#common-data-service/",
            priority="Low",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available') and deployment.get('has_users'):
            # Add actual capacity data from pp_client
            capacity_info = ""
            if pp_client and hasattr(pp_client, 'capacity_summary'):
                db_usage = pp_client.capacity_summary.get('database_usage_percent', 0)
                capacity_info = f" Currently using {db_usage:.0f}% of trial capacity."
            
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Trial Optimization",
                observation=f"Trial Dataverse environment ready for agent PoC.{capacity_info}",
                recommendation="Maximize trial Dataverse value: 1) Build 1-2 proof-of-concept agents to demonstrate value, 2) Keep data volume minimal (trial has storage limits), 3) Focus on showcasing agent capabilities rather than production scale, 4) Measure success metrics for business case, 5) Plan migration path to licensed Dataverse for production. Trial is for proving value, not production deployment - convert successful PoCs to licensed environments.",
                link_text="Trial Best Practices",
                link_url="https://learn.microsoft.com/power-platform/admin/trial-environments",
                priority="Low",
                status="Success"
            )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Trial Planning",
                observation="Trial Dataverse available for experimentation",
                recommendation="Use trial to build business case: Create simple agent PoC, gather feedback, document value, present to decision makers for license approval.",
                link_text="Dataverse Trials",
                link_url="https://learn.microsoft.com/power-platform/admin/trial-environments",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
