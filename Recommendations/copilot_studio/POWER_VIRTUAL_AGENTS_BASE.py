"""
Power Virtual Agents (Base) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name
from Core.get_power_platform_client import extract_pp_insights_from_client

async def get_deployment_status(client, pp_insights=None):
    """Check for basic agent deployment readiness with environment awareness."""
    try:
        sites = await client.sites.get()
        result = {'available': True, 'has_content': sites and sites.value and len(sites.value) > 0}
        
        if pp_insights:
            result['has_pp_access'] = True
            result['env_total'] = pp_insights.get('environments_total', 0)
            result['env_dev'] = 0  # Not in standard pp_insights
            result['env_sandbox'] = pp_insights.get('sandbox_envs', 0)
            result['env_prod'] = pp_insights.get('production_envs', 0)
            result['apps_total'] = pp_insights.get('apps_total', 0)
            result['canvas_apps'] = pp_insights.get('canvas_apps', 0)
            result['teams_apps'] = pp_insights.get('teams_apps', 0)
            result['premium_connectors'] = pp_insights.get('premium_connectors', 0)
            result['has_sql'] = pp_insights.get('has_sql', False)
            result['ai_models'] = pp_insights.get('ai_models_total', 0)
            
            # Build environment description
            env_types = []
            if result['env_prod'] > 0:
                env_types.append(f"{result['env_prod']} production")
            if result['env_sandbox'] > 0:
                env_types.append(f"{result['env_sandbox']} sandbox")
            if result['env_dev'] > 0:
                env_types.append(f"{result['env_dev']} developer")
            result['env_desc'] = ', '.join(env_types) if env_types else f"{result['env_total']} environment(s)"
        
        return result
    except Exception as e:
        return {'available': False, 'reason': str(e)}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Virtual Agents Base provides foundational chatbot capabilities.
    Returns 2 recommendations: license status + deployment readiness.
    """
    feature_name = "Power Virtual Agents (Base)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing base agent creation capabilities within Copilot Studio",
            recommendation="",
            link_text="Copilot Studio Base Features",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing foundational agent building capabilities",
            recommendation=f"Enable {feature_name} to access base-level Copilot Studio functionality for creating simple conversational agents. Base tier includes core conversation design tools, basic topic creation, and entity recognition sufficient for straightforward Q&A agents and information-gathering scenarios. While limited compared to premium Copilot Studio features, it provides entry point for organizations starting agent adoption. Suitable for simple HR policy chatbots, basic IT support agents, and FAQ automation before advancing to complex, action-oriented agents that require premium capabilities.",
            link_text="Copilot Studio Base Features",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            priority="Low",
            status=status
        )
    
    if status == "Success" and client:
        # Extract insights from pp_client if available
        pp_insights = extract_pp_insights_from_client(pp_client) if pp_client else None
        deployment = await get_deployment_status(client, pp_insights)
        if deployment.get('available') and deployment.get('has_content'):
            env_desc = deployment.get('env_desc', 'environment infrastructure')
            env_prod = deployment.get('env_prod', 0)
            env_dev = deployment.get('env_dev', 0)
            apps_total = deployment.get('apps_total', 0)
            teams_apps = deployment.get('teams_apps', 0)
            premium_conns = deployment.get('premium_connectors', 0)
            ai_models = deployment.get('ai_models', 0)
            
            pp_assets = []
            if apps_total > 0:
                pp_assets.append(f"{apps_total} app{'s' if apps_total != 1 else ''}")
            if teams_apps > 0:
                pp_assets.append(f"{teams_apps} in Teams")
            if premium_conns > 0:
                pp_assets.append(f"{premium_conns} premium connector{'s' if premium_conns != 1 else ''}")
            if ai_models > 0:
                pp_assets.append(f"{ai_models} AI model{'s' if ai_models != 1 else ''}")
            pp_desc = f", Power Platform: {', '.join(pp_assets)}" if pp_assets else ""
            
            if env_prod > 0:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - First Agent Development",
                    observation=f"Organization has SharePoint content and {env_desc}{pp_desc} - ready for foundational agent creation",
                    recommendation=f"Build first proof-of-concept agent in {'developer environment' if env_dev > 0 else 'sandbox'}: 1) Choose simple, high-frequency use case (office hours, location finder, basic policy lookup), 2) Use pre-built templates for common scenarios, 3) Connect to existing SharePoint FAQ list (no custom data source needed), 4) Test conversation flow with 3-5 pilot users, 5) Measure success: questions answered without escalation. Base tier provides core conversation design - sufficient for straightforward Q&A before investing in premium Copilot Studio capabilities. Start simple to validate agent value.",
                    link_text="Build First Agent",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/fundamentals-get-started",
                    priority="Low",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Environment Setup",
                    observation=f"SharePoint content available with {env_desc} - establish foundational agent environment",
                    recommendation="Set up production environment for agent deployment: Base capabilities work best with clear environment separation (dev for building, production for user access). Create simple FAQ agent as first project to learn platform before complex scenarios.",
                    link_text="Environment Setup",
                    link_url="https://learn.microsoft.com/power-platform/admin/environments-overview",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Getting Started",
                observation="Basic agent creation capabilities available",
                recommendation="Start agent journey: Create SharePoint knowledge base document, build first simple conversation flow using templates, test with small pilot group. Base tier is learning platform before advancing to complex, action-oriented agents.",
                link_text="Agent Tutorials",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/fundamentals-get-started",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
