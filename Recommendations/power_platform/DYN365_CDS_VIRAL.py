"""
Common Data Service (Viral) - Power Platform & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for Dynamics trial environment."""
    try:
        users = await client.users.get()
        return {'available': True, 'has_users': users and users.value and len(users.value) > 0}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Dynamics CDS Viral for trial agents.
    Returns 2 recommendations: license status + Dynamics trial optimization.
    """
    feature_name = "Common Data Service (Viral)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing data storage for Power Platform apps and flows that can integrate with Copilot",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to provide data storage and management capabilities for Power Platform apps and flows.",
            link_text="Common Data Service",
            link_url="https://learn.microsoft.com/power-apps/maker/data-platform/",
            priority="Medium",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            # Use real capacity data from pp_client if available
            capacity_info = ""
            if pp_client and hasattr(pp_client, 'capacity_summary'):
                db_usage = pp_client.capacity_summary.get('database_usage_percent', 0)
                capacity_info = f" Currently using {db_usage:.0f}% of trial capacity."
            
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Dynamics Trial",
                observation=f"Viral Dataverse license provides trial-grade storage for building proof-of-concept Dynamics agents (customer service bots, sales assistants) without upfront investment.{capacity_info}",
                recommendation="Use trial to explore Dynamics agents: Create simple customer service or sales assistant PoC querying trial D365 data. Demonstrate agent value for business case. Trial capacity is limited - focus on proving concept before requesting licensed Dynamics Dataverse. Build minimal viable agent to show stakeholders potential ROI.",
                link_text="Dynamics Trial Best Practices",
                link_url="https://learn.microsoft.com/dynamics365/",
                priority="Low",
                status="Success"
            )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Trial",
                observation="Viral Dataverse available for trials",
                recommendation="Experiment with basic Dataverse scenarios for agent prototyping.",
                link_text="Dataverse Trials",
                link_url="https://learn.microsoft.com/power-apps/maker/data-platform/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
