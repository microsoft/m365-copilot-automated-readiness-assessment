"""
Flow Virtual Agent Base Messages - Workflow Message Capacity Add-on
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name
from Core.get_power_platform_client import extract_pp_insights_from_client

async def get_deployment_status(client, pp_insights=None):
    """Check workflow message capacity infrastructure."""
    try:
        users = await client.users.get()
        result = {'available': True, 'user_count': len(users.value) if users and users.value else 0}
        
        if pp_insights:
            result['has_pp_access'] = True
            result['environments'] = pp_insights.get('environments_total', 0)
            result['flows_total'] = pp_insights.get('flows_total', 0)
        
        return result
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Flow Virtual Agent Base Messages - additional message capacity for workflow agents.
    Returns 2 recommendations: license status + automation message planning.
    """
    feature_name = "Flow Virtual Agent Base Messages"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, adding message capacity for Power Automate-integrated agents",
            recommendation="",
            link_text="Workflow Message Capacity",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/requirements-quotas",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to add message capacity for workflow-integrated agent conversations.",
            link_text="Message Capacity",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            priority="Low",
            status=status
        )
    
    if status == "Success" and client:
        # Extract insights from pp_client if available
        pp_insights = extract_pp_insights_from_client(pp_client) if pp_client else None
        deployment = await get_deployment_status(client, pp_insights)
        if deployment.get('available'):
            user_count = deployment.get('user_count', 0)
            env_count = deployment.get('environments', 0)
            flows_total = deployment.get('flows_total', 0)
            
            if user_count > 100:
                obs_parts = [f"{user_count} users"]
                if flows_total > 0:
                    obs_parts.append(f"{flows_total} workflow{'s' if flows_total != 1 else ''} (action-agent automation)")
                
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Workflow Message Planning",
                    observation=f"Action agent message capacity: {', '.join(obs_parts)} - workflow-triggered agents use more messages per session",
                    recommendation="Allocate workflow message capacity: Action agents (ticket creation, approvals) generate more messages per conversation than FAQ agents. Each workflow step (gather details → confirm → execute → notify) adds messages. Monitor message consumption for automation-heavy agents vs knowledge agents separately.",
                    link_text="Workflow Capacity",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/requirements-quotas",
                    priority="Low",
                    status="Success"
                )
            else:
                obs_parts = []
                if flows_total > 0:
                    obs_parts.append(f"{flows_total} workflow{'s' if flows_total != 1 else ''}")
                    obs_parts.append("workflow message capacity enables action agents (ticket creation, approval routing, system updates)")
                else:
                    obs_parts.append("workflow message capacity ready for action agents - build flows for automated business processes")
                
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Message Add-on",
                    observation=f"Action agent message capacity: {' - '.join(obs_parts)}",
                    recommendation="Use for action agents requiring multi-step conversations and workflow execution.",
                    link_text="Message Planning",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Capacity",
                observation="Workflow agent message capacity allocated - supports action agents that create tickets, route approvals, update CRM/ERP systems via Power Automate",
                recommendation="Monitor workflow agent message usage and scale capacity as automation grows.",
                link_text="Capacity Management",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
