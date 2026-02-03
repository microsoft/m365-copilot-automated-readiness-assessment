"""
Common Data Service for Copilot Studio - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for Copilot Studio agent readiness."""
    try:
        users = await client.users.get()
        return {'available': True, 'user_count': len(users.value) if users and users.value else 0}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Dataverse for Copilot Studio agents.
    Returns 2 recommendations: license status + agent deployment.
    """
    feature_name = "Common Data Service for Copilot Studio"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing data persistence for agent conversations and context",
            recommendation="",
            link_text="Dataverse for Agent State Management",
            link_url="https://learn.microsoft.com/power-apps/maker/data-platform/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing agents from maintaining context and accessing structured data",
            recommendation=f"Enable {feature_name} to give Copilot Studio agents access to structured business data. Store agent conversation histories so agents remember previous interactions, maintain user preferences and context across sessions, and query business data through natural language. For example, an HR agent can access employee records in Dataverse to answer 'How many PTO days do I have left?' This transforms agents from stateless chatbots into context-aware assistants that provide personalized, data-driven responses.",
            link_text="Dataverse for Agent State Management",
            link_url="https://learn.microsoft.com/power-apps/maker/data-platform/",
            priority="High",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            user_count = deployment.get('user_count', 0)
            if user_count > 100:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Agent Deployment",
                    observation=f"Organization with {user_count} users ready for Copilot Studio agents",
                    recommendation="Deploy Copilot Studio agents with Dataverse: 1) Build HR agent that queries Dataverse tables for PTO balances, org charts, policies, 2) Create IT helpdesk agent accessing ticket history, asset inventory, FAQ database, 3) Deploy procurement agent with supplier data, purchase history, approval workflows. Dataverse stores agent conversation context enabling multi-turn interactions, remembers user preferences, maintains state across sessions. Agents become stateful assistants rather than one-off Q&A.",
                    link_text="Build Agents with Dataverse",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                    priority="High",
                    status="Success"
                )
            else:
                # Use real capacity and app data from pp_insights if available
                context_info = ""
                if pp_client and hasattr(pp_client, 'capacity_summary'):
                    db_usage = pp_client.capacity_summary.get('database_usage_percent', 0)
                    context_info = f" Database usage at {db_usage:.0f}%."
                if pp_insights:
                    total_apps = pp_insights.get('apps_total', 0)
                    if total_apps > 0:
                        context_info += f" {total_apps} app(s) can provide data context to agents."
                
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - First Agent",
                    observation=f"Dataverse bundled with Copilot Studio stores agent conversation history, user context, and entity data - enabling intelligent, personalized responses that remember past interactions.{context_info}",
                    recommendation="Build first agent with Dataverse context: Choose simple scenario (FAQ agent, status lookup), store data in Dataverse, enable conversational queries.",
                    link_text="Getting Started",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                    priority="Medium",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Agent Planning",
                observation="Dataverse for agents available",
                recommendation="Identify agent scenarios requiring persistent data and conversation context storage.",
                link_text="Copilot Studio",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
