"""
CDS Virtual Agent Base Messages - Dataverse Message Capacity Add-on
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name
from get_power_platform_client import extract_pp_insights_from_client

async def get_deployment_status(client, pp_insights=None):
    """Check Dataverse message capacity infrastructure."""
    try:
        users = await client.users.get()
        result = {'available': True, 'user_count': len(users.value) if users and users.value else 0}
        
        if pp_insights:
            result['has_pp_access'] = True
            result['environments'] = pp_insights.get('environments_total', 0)
            result['env_production'] = pp_insights.get('production_envs', 0)
            result['model_driven_apps'] = pp_insights.get('model_driven_apps', 0)
        
        return result
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    CDS Virtual Agent Base Messages - additional Dataverse-connected message capacity.
    Returns 2 recommendations: license status + Dataverse message planning.
    """
    feature_name = "CDS Virtual Agent Base Messages"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, adding message capacity for Dataverse-connected agents",
            recommendation="",
            link_text="Dataverse Message Capacity",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/requirements-quotas",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to add message volume capacity for entity-driven agent conversations.",
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
            has_pp = deployment.get('has_pp_access', False)
            model_apps = deployment.get('model_driven_apps', 0)
            
            if has_pp and env_count > 0:
                obs_parts = [f"{user_count} users", f"{env_count} environment{'s' if env_count != 1 else ''}"]
                if model_apps > 0:
                    obs_parts.append(f"{model_apps} model-driven app{'s' if model_apps != 1 else ''} (Dataverse entity access)")
                
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Dataverse Message Planning",
                    observation=f"Entity-driven agent message capacity: {', '.join(obs_parts)} - Dataverse queries consume additional messages",
                    recommendation=f"Allocate Dataverse message capacity: 1) Prioritize entity-heavy agents (customer lookup requiring multiple Dataverse queries consumes more messages than simple FAQ), 2) Monitor message consumption for Dataverse-connected agents separately from standard agents, 3) Plan capacity for data-driven conversations requiring entity operations. Entity-accessing agents use more messages per conversation. Track per-environment message usage.",
                    link_text="Dataverse Messages",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/requirements-quotas",
                    priority="Low",
                    status="Success"
                )
            else:
                obs_parts = [f"{user_count} users"]
                if model_apps > 0:
                    obs_parts.append(f"{model_apps} model-driven app{'s' if model_apps != 1 else ''}")
                    obs_parts.append("Dataverse message capacity supports agents querying customer records, cases, inventory data")
                else:
                    obs_parts.append("Dataverse message capacity ready - enables agents to access Dataverse tables (Accounts, Contacts, custom entities)")
                
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Message Capacity",
                    observation=f"Entity-driven agent message capacity: {' - '.join(obs_parts)}",
                    recommendation="Use additional capacity for entity-driven agent scenarios requiring higher message volumes.",
                    link_text="Message Planning",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Capacity Add-on",
                observation="Additional message capacity available",
                recommendation="Monitor Dataverse agent message consumption and allocate additional capacity as needed.",
                link_text="Capacity Management",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
