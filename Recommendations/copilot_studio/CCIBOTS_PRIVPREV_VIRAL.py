"""
Copilot Studio (Viral) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name
from Core.get_power_platform_client import extract_pp_insights_from_client

async def get_deployment_status(client, pp_insights=None):
    """Check if trial environment infrastructure supports proof-of-concept development."""
    try:
        sites = await client.sites.get()
        result = {'available': True, 'has_content': sites and sites.value and len(sites.value) > 0}
        
        if pp_insights:
            result['has_pp_access'] = True
            result['env_total'] = pp_insights.get('environments_total', 0)
            result['env_trial'] = pp_insights.get('trial_envs', 0)
            result['env_dev'] = 0  # Not in standard pp_insights
            result['env_default'] = 0  # Not in standard pp_insights
            result['flows_total'] = pp_insights.get('flows_total', 0)
            result['apps_total'] = pp_insights.get('apps_total', 0)
            
            # Build trial environment description
            trial_count = result['env_trial'] + result['env_dev'] + result['env_default']
            result['trial_desc'] = f"{trial_count} trial/dev environment(s)" if trial_count > 0 else "trial access"
        
        return result
    except Exception as e:
        return {'available': False, 'reason': str(e)}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Copilot Studio Viral provides trial access for experimentation.
    Returns 2 recommendations: license status + trial optimization.
    """
    feature_name = "Copilot Studio (Viral)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling trial agent development and experimentation",
            recommendation="",
            link_text="Trial Copilot Studio Access",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting ability to trial custom agent creation",
            recommendation=f"Enable {feature_name} to provide trial access to Copilot Studio for prototyping custom agents without licensing delays. Viral access allows developers and business users to experiment with agent design, test conversation flows, and validate use cases before requesting full licenses. Build proof-of-concept agents for management approval, enable citizen developers to explore agent possibilities, and conduct pilots to measure agent effectiveness. Trial period helps organizations understand agent capabilities and identify high-value scenarios before enterprise-wide deployment and investment.",
            link_text="Trial Copilot Studio Access",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            priority="Low",
            status=status
        )
    
    if status == "Success" and client:
        # Extract insights from pp_client if available
        pp_insights = extract_pp_insights_from_client(pp_client) if pp_client else None
        deployment = await get_deployment_status(client, pp_insights)
        if deployment.get('available') and deployment.get('has_content'):
            trial_desc = deployment.get('trial_desc', 'trial access')
            trial_count = deployment.get('env_trial', 0) + deployment.get('env_dev', 0) + deployment.get('env_default', 0)
            
            if trial_count > 0:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Proof-of-Concept Strategy",
                    observation=f"SharePoint content available with {trial_desc} - structured trial for agent value demonstration",
                    recommendation=f"Maximize trial period ROI with focused proof-of-concept: 1) Build 1 high-impact demo agent using existing SharePoint FAQ content (no data prep delays), 2) Choose visible use case: IT helpdesk (common password/access questions) or HR support (PTO policies, benefits), 3) Run 2-week pilot with 10-15 real users from target department, 4) Collect metrics: conversations handled, questions answered without human escalation, user satisfaction scores, time saved for support team, 5) Calculate ROI: (support hours saved × hourly cost) vs license cost, 6) Present business case to leadership with pilot data and 3-5 identified production use cases. Trial environments are temporary - focus on proving value and securing production licenses, not building production-ready solutions. Time-box trial to 30 days: 1 week setup, 2 weeks pilot, 1 week analysis and presentation.",
                    link_text="Trial Best Practices",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/sign-up-individual",
                    priority="Low",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Trial Setup",
                    observation="SharePoint content available - establish trial environment for agent experimentation",
                    recommendation="Set up trial environment: Create developer or default environment for building proof-of-concept agents. Use existing content to build demo quickly and prove agent value to stakeholders.",
                    link_text="Trial Environment Setup",
                    link_url="https://learn.microsoft.com/power-platform/admin/trial-environments",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Trial Planning",
                observation="Trial license active - build 1-2 proof-of-concept agents (IT helpdesk, HR FAQ) to demonstrate ROI: measure question deflection rate, calculate support hours saved, present business case to leadership for production licenses",
                recommendation="Plan trial strategy: Use trial period to build business case for Copilot Studio investment. Create 1-2 focused demo agents, run small pilot with real users, measure deflection rate and time savings, document ROI, present to decision makers for production license approval. Trial is validation phase, not production deployment.",
                link_text="Trial Getting Started",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/sign-up-individual",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
