"""
Common Data Service for Office 365 (Plan 3) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for premium Dynamics agent opportunities."""
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
    Dynamics CDS P3 enables premium agent capabilities.
    Returns 2 recommendations: license status + premium Dynamics agents.
    """
    feature_name = "Common Data Service for Office 365 (Plan 3) - Dynamics"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing structured data storage for agent context and workflows",
            recommendation="",
            link_text="Store Agent Data in Dataverse",
            link_url="https://learn.microsoft.com/power-apps/maker/data-platform/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, lacking enterprise data platform for agents",
            recommendation=f"Enable {feature_name} to provide the data foundation for enterprise agents. Store structured business data that agents can query through natural language, maintain conversation histories for contextual AI interactions, build custom knowledge bases that extend Copilot's understanding of your business, and create secure data models that agents use to perform actions. Dataverse integration enables agents to move beyond read-only assistance to actually managing business processes.",
            link_text="Store Agent Data in Dataverse",
            link_url="https://learn.microsoft.com/power-apps/maker/data-platform/",
            priority="High",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            user_count = deployment.get('user_count', 0)
            has_data = deployment.get('has_data', False)
            
            if user_count > 500 and has_data:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Enterprise Dynamics AI",
                    observation=f"Enterprise Dynamics deployment ({user_count} users) with data - ready for AI-powered agents",
                    recommendation="Build premium Dynamics agents with AI Builder: 1) Create intelligent customer service agent using AI sentiment analysis on case comments, entity extraction from emails, custom ML models for case routing, 2) Deploy sales copilot with AI-powered lead scoring, opportunity risk prediction, next-best-action recommendations, 3) Build field service agent with predictive maintenance models, image recognition for equipment diagnosis. Plan 3 includes AI Builder capacity for premium agent capabilities beyond basic Q&A - agents that predict, classify, and intelligently route. Integrate with SharePoint knowledge for comprehensive context.",
                    link_text="AI-Powered Dynamics Agents",
                    link_url="https://learn.microsoft.com/ai-builder/",
                    priority="High",
                    status="Success"
                )
            elif user_count > 500:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Enterprise Dynamics Agents",
                    observation=f"Large Dynamics organization ({user_count} users) ready for enterprise agents",
                    recommendation="Deploy enterprise Dynamics agents: Customer service copilot for case management, sales assistant for pipeline intelligence, operations agent for workflow automation. Plan 3 provides premium capacity and AI Builder for advanced scenarios.",
                    link_text="Enterprise Dynamics Agents",
                    link_url="https://learn.microsoft.com/dynamics365/customer-service/administer/copilot-overview",
                    priority="Medium",
                    status="Success"
                )
            else:
                # Use real AI Builder data from pp_insights if available
                ai_info = ""
                if pp_insights:
                    total_models = pp_insights.get('ai_models_total', 0)
                    if total_models > 0:
                        ai_info = f" You have {total_models} AI Builder model(s) ready for agent integration."
                    else:
                        ai_info = " No AI Builder models created yet - excellent opportunity to leverage included credits."
                
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Premium Agents",
                    observation=f"Plan 3 Dataverse includes AI Builder credits for building intelligent Copilot extensions - create agents that analyze sentiment, extract entities, predict outcomes from Dynamics data.{ai_info}",
                    recommendation="Leverage Plan 3 premium features: Build AI-enhanced agents with sentiment analysis, entity extraction, custom models for Dynamics workflows.",
                    link_text="Premium Agent Features",
                    link_url="https://learn.microsoft.com/ai-builder/",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Premium Planning",
                observation="Premium Dataverse for Dynamics available",
                recommendation="Plan premium Dynamics agent scenarios leveraging AI Builder and advanced Dataverse capabilities.",
                link_text="Premium Dataverse",
                link_url="https://learn.microsoft.com/power-apps/maker/data-platform/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
