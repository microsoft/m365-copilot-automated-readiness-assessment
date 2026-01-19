"""
Common Data Service for Power Virtual Agents - Dataverse-integrated Agent Session Licensing
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client, pp_insights=None):
    """
    Check Dataverse-integrated agent session capacity planning.
    """
    try:
        import asyncio
        
        result = {
            'available': True,
            'user_count': 0,
            'has_teams': False,
            'team_count': 0,
            'environments': 0,
            'has_pp_access': False,
            'env_production': 0,
            'env_sandbox': 0,
            'env_developer': 0
        }
        
        tasks = [client.users.get(), client.groups.get()]
        
        # Use pre-computed Power Platform insights
        if pp_insights:
            result['has_pp_access'] = True
            result['environments'] = pp_insights.get('environments_total', 0)
            result['env_production'] = pp_insights.get('production_envs', 0)
            result['env_sandbox'] = pp_insights.get('sandbox_envs', 0)
            result['env_developer'] = 0  # Not in standard pp_insights
            result['model_driven_apps'] = pp_insights.get('model_driven_apps', 0)
            result['connections_total'] = pp_insights.get('connections_total', 0)
        
        users, groups = await asyncio.gather(*tasks, return_exceptions=True)
        
        if not isinstance(users, Exception) and users and users.value:
            result['user_count'] = len(users.value)
        
        if not isinstance(groups, Exception) and groups and groups.value:
            teams = [g for g in groups.value if hasattr(g, 'resource_provisioning_options') 
                    and g.resource_provisioning_options 
                    and 'Team' in g.resource_provisioning_options]
            result['team_count'] = len(teams)
            result['has_teams'] = len(teams) > 0
        
        return result
            
    except Exception as e:
        return {'available': False, 'error': str(e)}
async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    CDS Virtual Agent USL - Dataverse-integrated agent sessions with entity data access.
    Returns 2 recommendations: license status + Dataverse session capacity strategy.
    """
    feature_name = "CDS Virtual Agent User Session"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Dataverse-connected agent sessions with entity data access",
            recommendation="",
            link_text="Dataverse for Agents",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing Dataverse entity integration for agents",
            recommendation=f"Enable {feature_name} to build agents that read/write Dataverse entities (customer records, cases, inventory, custom tables). Essential for CRM-connected agents, service desk automation, data-driven workflows.",
            link_text="Dataverse Agent Sessions",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            priority="Medium",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client, pp_insights)
        
        if deployment.get('available'):
            user_count = deployment.get('user_count', 0)
            team_count = deployment.get('team_count', 0)
            env_count = deployment.get('environments', 0)
            has_pp = deployment.get('has_pp_access', False)
            env_prod = deployment.get('env_production', 0)
            env_sandbox = deployment.get('env_sandbox', 0)
            env_dev = deployment.get('env_developer', 0)
            
            if has_pp and env_count > 0:
                # Build environment description
                env_desc = []
                if env_prod > 0:
                    env_desc.append(f"{env_prod} production")
                if env_sandbox > 0:
                    env_desc.append(f"{env_sandbox} sandbox")
                if env_dev > 0:
                    env_desc.append(f"{env_dev} developer")
                env_types = ", ".join(env_desc) if env_desc else ("1 environment" if env_count == 1 else f"{env_count} environments")
                
                if user_count > 200:
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Dataverse Session Planning",
                        observation=f"Organization ready for entity-driven agents: {user_count} users, {env_types} with Dataverse",
                        recommendation=f"Plan Dataverse-integrated agent sessions using {env_types}: 1) Build agents that query/update Dataverse entities: customer service (case creation, account lookup), inventory (stock checks, order updates), HR (employee records, leave requests), 2) {'Use dev/sandbox Dataverse for entity schema testing, production for live data operations' if env_prod > 0 else 'Test entity operations in current environments, establish production Dataverse for enterprise deployment'}, 3) Estimate concurrent sessions needing Dataverse access: {user_count} × 5% = ~{int(user_count * 0.05)} potential entity-accessing sessions, 4) Monitor Dataverse API limits per environment (requests/day), session duration accessing entities, 5) {'Separate Dataverse environments by function: customer data in prod1, internal HR in prod2' if env_prod > 1 else 'Plan Dataverse capacity for agent entity operations'}. CDS USL enables agents to be data-driven, not just conversational. Target: 2-3 entity-integrated agents within 60 days.",
                        link_text="Dataverse Agent Integration",
                        link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-entities-slot-filling",
                        priority="High",
                        status="Success"
                    )
                else:
                    # Build observation with Dataverse infrastructure
                    model_driven_apps = deployment.get('model_driven_apps', 0)
                    connections = deployment.get('connections_total', 0)
                    
                    obs_parts = [f"{user_count} users", env_types]
                    if model_driven_apps > 0:
                        obs_parts.append(f"{model_driven_apps} model-driven app{'s' if model_driven_apps != 1 else ''} (Dataverse entities available for agents)")
                    else:
                        obs_parts.append("no model-driven apps yet (opportunity: agents can still access Dataverse tables directly)")
                    
                    if connections > 0:
                        obs_parts.append(f"{connections} connection{'s' if connections != 1 else ''} (entity integration options)")
                    
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Entity-Connected Sessions",
                        observation=f"Dataverse agent infrastructure: {', '.join(obs_parts)} - agents can query/update business entities",
                        recommendation=f"Build entity-driven agents using {env_types}: 1) Create agents that access Dataverse tables (Accounts, Contacts, custom entities), 2) {'Use dev/sandbox for entity schema development, production for user-facing data operations' if env_prod > 0 else 'Develop entity integration patterns in current environments'}, 3) Track session metrics: entity operations/session, Dataverse API consumption, data access latency. CDS USL sessions can read/write business data, enabling true automation. Target: First entity-integrated agent within 45 days.",
                        link_text="Dataverse Entities in Agents",
                        link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-entities-slot-filling",
                        priority="Medium",
                        status="Success"
                    )
            else:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Dataverse Planning",
                    observation="CDS agent sessions available for entity integration",
                    recommendation="Plan Dataverse-connected agents: Identify entity-driven scenarios (customer lookup, case creation, inventory checks), estimate sessions needing data access, monitor Dataverse API limits. Request Power Platform admin access for environment-specific entity planning.",
                    link_text="Dataverse for Agents",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                    priority="Medium",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Session Planning",
                observation="Dataverse agent sessions available",
                recommendation="Explore entity-driven agent scenarios: Build agents that read/write Dataverse tables for automated data operations.",
                link_text="Dataverse Integration",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
