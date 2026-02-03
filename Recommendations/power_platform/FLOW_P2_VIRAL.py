"""
Power Automate (Free) - Power Platform & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for automation trial opportunities."""
    try:
        org = await client.organization.get()
        return {'available': True, 'has_org': org and org.value}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Automate trial for workflow experiments.
    Returns 2 recommendations: license status + trial workflow guidance.
    """
    feature_name = "Power Automate (Free)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling workflow automation that can be triggered by Copilot and agents",
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
            recommendation=f"Enable {feature_name} to provide basic workflow automation capabilities for users.",
            link_text="Power Automate",
            link_url="https://learn.microsoft.com/power-automate/",
            priority="Medium",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            # Use real flow data from pp_insights if available
            flow_info = ""
            if pp_insights:
                total_flows = pp_insights.get('flows_total', 0)
                http_flows = pp_insights.get('http_triggers', 0)
                if total_flows > 0:
                    flow_info = f" You have {total_flows} flow(s) ({http_flows} with HTTP triggers for Copilot integration)."
                else:
                    flow_info = " No flows created yet - ideal time to start with agent-triggered automation."
            
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Trial Workflows",
                observation=f"Free Power Automate tier lets you prototype Copilot-triggered workflows (send emails, create Teams messages when user prompts agent) to prove automation value before purchasing licenses.{flow_info}",
                recommendation="Use free tier to test agent automation scenarios: Create simple flow triggered by agent (send email, create Teams message), understand agent + workflow integration before requesting premium licenses. Trial demonstrates ROI for licensed automation. Limitations: Limited runs per month, no premium connectors - sufficient for PoC but not production.",
                link_text="Trial Automation",
                link_url="https://learn.microsoft.com/power-automate/",
                priority="Low",
                status="Success"
            )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Experimentation",
                observation="Free automation tier available",
                recommendation="Experiment with basic agent-triggered workflows to understand automation value.",
                link_text="Power Automate Basics",
                link_url="https://learn.microsoft.com/power-automate/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
