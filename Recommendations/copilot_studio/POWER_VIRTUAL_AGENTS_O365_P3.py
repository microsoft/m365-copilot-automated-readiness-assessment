"""
Power Virtual Agents for Office 365 - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name
from Core.get_power_platform_client import extract_pp_insights_from_client

async def get_deployment_status(client, pp_insights=None):
    """Check Teams availability for agent deployment with environment awareness."""
    try:
        teams_activity = await client.reports.get_teams_user_activity_counts(period='D7').get()
        result = {
            'available': True,
            'has_teams': teams_activity and teams_activity.value and len(teams_activity.value) > 0
        }
        
        if pp_insights:
            result['has_pp_access'] = True
            result['env_total'] = pp_insights.get('environments_total', 0)
            result['env_prod'] = pp_insights.get('production_envs', 0)
            result['env_sandbox'] = pp_insights.get('sandbox_envs', 0)
            result['apps_total'] = pp_insights.get('apps_total', 0)
            result['teams_apps'] = pp_insights.get('teams_apps', 0)
            
            # Build environment description
            env_types = []
            if result['env_prod'] > 0:
                env_types.append(f"{result['env_prod']} production")
            if result['env_sandbox'] > 0:
                env_types.append(f"{result['env_sandbox']} sandbox")
            result['env_desc'] = ', '.join(env_types) if env_types else f"{result['env_total']} environment(s)"
        
        return result
    except Exception as e:
        return {'available': False, 'reason': str(e)}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Virtual Agents for Office 365 provides chatbot capabilities for M365.
    Returns 2 recommendations: license status + Teams integration.
    """
    feature_name = "Power Virtual Agents for Office 365"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling intelligent chatbot creation for common employee scenarios",
            recommendation="",
            link_text="Create Support Bots with Copilot Studio",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/fundamentals-what-is-power-virtual-agents",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing conversational AI capabilities for employee support",
            recommendation=f"Enable {feature_name} to create conversational agents that handle common employee requests (IT support, HR questions, facilities issues) before escalating to humans. Build chatbots that integrate with your existing M365 environment, leverage generative AI for natural conversations, and reduce the load on support teams. These agents complement M365 Copilot by providing specialized, task-oriented assistance while Copilot handles broader productivity scenarios.",
            link_text="Create Support Bots with Copilot Studio",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/fundamentals-what-is-power-virtual-agents",
            priority="Medium",
            status=status
        )
    
    if status == "Success" and client:
        # Extract insights from pp_client if available
        pp_insights = extract_pp_insights_from_client(pp_client) if pp_client else None
        deployment = await get_deployment_status(client, pp_insights)
        if deployment.get('available') and deployment.get('has_teams'):
            env_desc = deployment.get('env_desc', 'environment infrastructure')
            env_prod = deployment.get('env_prod', 0)
            apps_total = deployment.get('apps_total', 0)
            teams_apps = deployment.get('teams_apps', 0)
            
            # Build observation with Teams context
            teams_obs_parts = [f"Teams active with {env_desc}"]
            if teams_apps > 0:
                teams_obs_parts.append(f"{teams_apps} Teams-integrated app{'s' if teams_apps != 1 else ''} (add conversational layer)")
            elif apps_total > 0:
                teams_obs_parts.append(f"{apps_total} app{'s' if apps_total != 1 else ''} (Teams deployment opportunity)")
            
            if env_prod > 0:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Teams Agent Deployment",
                    observation=f"{' - '.join(teams_obs_parts)} - M365 agent channel ready",
                    recommendation=f"Deploy specialized M365 support agents directly in Teams: 1) IT Helpdesk Agent - password resets (Entra ID integration), software access requests (Azure AD app registration), VPN troubleshooting (knowledge from SharePoint IT docs). Deploy to #it-support channel, 2) HR Agent - PTO policies (SharePoint policy library), benefits enrollment (link to HR portal), onboarding checklist (new hire Planner tasks). Deploy to #hr-questions channel, 3) Measure deflection: % of questions answered without @mentioning human support, 4) Track adoption: conversations per week, unique users, resolution rate. Teams integration eliminates agent deployment friction - employees use existing chat interface, no app downloads, conversations in daily workflow context.",
                    link_text="Deploy Agents to Teams",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/publication-add-bot-to-microsoft-teams",
                    priority="Medium",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Teams Readiness",
                    observation=f"Teams active with {env_desc} - establish production environment for agent deployment",
                    recommendation="Set up production environment for Teams agent deployment: Build agents in sandbox, test conversation flows with pilot team, deploy to production for organization-wide access. Teams is primary agent channel for Office 365 scenarios.",
                    link_text="Teams Deployment",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/publication-add-bot-to-microsoft-teams",
                    priority="Medium",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Deployment Planning",
                observation="M365-integrated agent capabilities ready - build support agents for Teams/SharePoint (IT helpdesk: password resets, HR: PTO policies, Facilities: room booking) to deflect repetitive questions from support staff",
                recommendation="Plan M365-integrated agent strategy: Identify repetitive support requests (IT, HR, facilities), build specialized agents for each domain, deploy to Teams/SharePoint/email channels. Focus on deflecting simple questions to free support staff for complex issues.",
                link_text="Agent Deployment Options",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/publication-fundamentals-publish-channels",
                priority="Medium",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
