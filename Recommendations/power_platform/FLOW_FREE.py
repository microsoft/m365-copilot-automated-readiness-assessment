"""
Power Automate (Free) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check readiness for basic automation."""
    try:
        org = await client.organization.get()
        return {'available': True, 'has_org': org and org.value}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Automate Free provides limited automation for trials.
    Returns 2 recommendations: license status + learning guidance.
    """
    feature_name = "Power Automate (Free)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling basic automation for agent prototyping",
            recommendation="",
            link_text="Free Automation Tier",
            link_url="https://learn.microsoft.com/power-automate/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting trial automation capabilities for agents",
            recommendation=f"Enable {feature_name} to provide basic Power Automate capabilities for prototyping agent-triggered workflows. Free tier allows limited flow runs per month, suitable for testing how agents can initiate approvals, send notifications, or update records. While restricted compared to licensed Power Automate, it enables experimentation with action-oriented agents before investment. Use it to demonstrate agent value in scenarios like 'approve my vacation request' or 'create ticket for this issue' before scaling to premium automation capabilities.",
            link_text="Free Automation Tier",
            link_url="https://learn.microsoft.com/power-automate/",
            priority="Low",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            # Add actual flow data from pp_insights
            flow_info = ""
            if pp_insights:
                total_flows = pp_insights.get('flows_total', 0)
                if total_flows > 0:
                    flow_info = f" You have {total_flows} flow(s) created."
                else:
                    flow_info = " No flows created yet - good starting point for learning."
            
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Learning",
                observation=f"Free automation tier available for learning and experimentation.{flow_info}",
                recommendation="Use free tier to learn automation: 1) Build simple flow triggered by agent (send email notification), 2) Test agent + workflow integration patterns, 3) Understand limits before requesting licenses, 4) Create PoC showing agent automation value. Free tier is stepping stone to licensed automation - use it to build business case and gain skills.",
                link_text="Learn Power Automate",
                link_url="https://learn.microsoft.com/training/powerplatform/power-automate",
                priority="Low",
                status="Success"
            )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Experimentation",
                observation="Free automation available",
                recommendation="Experiment with basic automation scenarios to understand Power Automate capabilities before licensing decisions.",
                link_text="Power Automate Basics",
                link_url="https://learn.microsoft.com/power-automate/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
