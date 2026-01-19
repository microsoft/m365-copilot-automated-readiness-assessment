"""
Power Automate for Copilot Studio - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for agent workflow readiness."""
    try:
        import asyncio
        users_task = client.users.get()
        sites_task = client.sites.get()
        
        users, sites = await asyncio.gather(users_task, sites_task, return_exceptions=True)
        
        result = {'available': True, 'user_count': 0, 'has_data': False}
        if not isinstance(users, Exception) and users and users.value:
            result['user_count'] = len(users.value)
        if not isinstance(sites, Exception) and sites and sites.value:
            result['has_data'] = len(sites.value) > 0
        return result
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Automate for Copilot Studio enables action agents.
    Returns 2 recommendations: license status + agent automation deployment.
    """
    feature_name = "Power Automate for Copilot Studio"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling agents to trigger automated workflows and actions",
            recommendation="",
            link_text="Agent Workflows with Power Automate",
            link_url="https://learn.microsoft.com/power-automate/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting agents to read-only responses",
            recommendation=f"Enable {feature_name} to transform Copilot Studio agents from informational chatbots into action-oriented assistants. Connect agent conversations to Power Automate flows that create help desk tickets, update CRM records, trigger approval processes, send notifications, and interact with hundreds of business systems. This is what makes agents valuable - they don't just answer questions, they get work done. A user can tell an agent 'Submit my time off request' and the agent executes the workflow, rather than just explaining the process.",
            link_text="Agent Workflows with Power Automate",
            link_url="https://learn.microsoft.com/power-automate/",
            priority="High",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            user_count = deployment.get('user_count', 0)
            has_data = deployment.get('has_data', False)
            
            if user_count > 100 and has_data:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Action Agents",
                    observation=f"Organization with {user_count} users and data - ready for action-oriented agents",
                    recommendation="Deploy action agents with Power Automate: 1) Build 'IT Helpdesk Agent' that creates service tickets in ServiceNow/Jira when user reports issue, 2) Create 'HR Assistant' that triggers PTO approval workflows, updates employee records in Dataverse/HRIS, 3) Deploy 'Procurement Agent' that submits purchase requests, routes approvals, sends notifications. Each agent connects to Power Automate flows for backend actions. Agents go from 'How do I...' to 'I did it for you' - transforming productivity. Target: 3-5 action agents replacing manual form submissions within 90 days.",
                    link_text="Build Action Agents",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
                    priority="High",
                    status="Success"
                )
            elif user_count > 100:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Agent Automation",
                    observation="Large user base ready for agent automation",
                    recommendation="Build first action agent: Choose common request (PTO, ticket creation, data lookup), create Power Automate flow, connect to Copilot Studio agent for conversational interface.",
                    link_text="Agent Automation",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
                    priority="Medium",
                    status="Success"
                )
            else:
                # Use real flow data from pp_insights if available
                flow_info = ""
                if pp_insights:
                    total_flows = pp_insights.get('flows_total', 0)
                    http_flows = pp_insights.get('http_triggers', 0)
                    if total_flows > 0:
                        flow_info = f" You have {total_flows} existing flow(s) ({http_flows} agent-callable) to build on."
                    else:
                        flow_info = " No flows yet - start with simple agent action like 'send email' or 'create Teams message'."
                
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - First Action Agent",
                    observation=f"Power Automate bundled with Copilot Studio enables agents to trigger multi-step workflows (create tickets, update CRM, send approvals) when users request actions in conversation.{flow_info}",
                    recommendation="Create first agent workflow: Simple action like send email, create Teams message, update list when agent detects intent.",
                    link_text="Getting Started",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Planning",
                observation="Power Automate for agents available",
                recommendation="Identify action scenarios where agents should trigger workflows: ticket creation, approvals, notifications, data updates.",
                link_text="Agent Workflows",
                link_url="https://learn.microsoft.com/power-automate/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
