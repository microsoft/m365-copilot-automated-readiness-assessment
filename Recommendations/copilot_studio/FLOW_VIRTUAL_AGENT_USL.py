"""
Flow Virtual Agent USL - Power Automate-integrated Agent Session Licensing
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client, pp_insights=None):
    """
    Check Power Automate-integrated agent session infrastructure.
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
            'env_developer': 0,
            'flows_total': 0,
            'cloud_flows': 0,
            'suspended_flows': 0,
            'premium_connectors': [],
            'has_sap': False,
            'has_salesforce': False,
            'has_servicenow': False,
            'custom_connectors': []
        }
        
        tasks = [client.users.get(), client.groups.get()]
        
        # Use pre-computed Power Platform insights
        if pp_insights:
            result['has_pp_access'] = True
            result['environments'] = pp_insights.get('environments_total', 0)
            result['env_production'] = pp_insights.get('production_envs', 0)
            result['env_sandbox'] = pp_insights.get('sandbox_envs', 0)
            result['env_developer'] = 0  # Not in pp_insights standard set
            result['flows_total'] = pp_insights.get('flows_total', 0)
            result['cloud_flows'] = pp_insights.get('cloud_flows', 0)
            result['suspended_flows'] = pp_insights.get('suspended_flows', 0)
            result['premium_connectors'] = []  # Would need to be added to pp_insights if needed
            result['has_sap'] = pp_insights.get('has_sap', False)
            result['has_salesforce'] = pp_insights.get('has_salesforce', False)
            result['has_servicenow'] = pp_insights.get('has_servicenow', False)
            result['custom_connectors'] = []  # Would need pp_insights enhancement
        
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
    Flow Virtual Agent USL - Power Automate workflow-triggered agent sessions.
    Returns 2 recommendations: license status + automation-driven session strategy.
    """
    feature_name = "Flow Virtual Agent User Session"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Power Automate workflow-integrated agent sessions",
            recommendation="",
            link_text="Flow Agent Integration",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing workflow automation for agents",
            recommendation=f"Enable {feature_name} to build agents that trigger Power Automate flows (create tickets, submit approvals, update systems). Essential for action-oriented agents that complete tasks, not just answer questions.",
            link_text="Agent Flow Integration",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
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
            
            # Extract Power Platform flow and connector data
            flows_total = deployment.get('flows_total', 0)
            suspended_flows = deployment.get('suspended_flows', 0)
            has_sap = deployment.get('has_sap', False)
            has_salesforce = deployment.get('has_salesforce', False)
            has_servicenow = deployment.get('has_servicenow', False)
            custom_conns = deployment.get('custom_connectors', [])
            
            # Build enterprise systems list
            enterprise_systems = [s for s, has in [('SAP', has_sap), ('Salesforce', has_salesforce), ('ServiceNow', has_servicenow)] if has]
            
            if has_pp and env_count > 0:
                env_desc = []
                if env_prod > 0:
                    env_desc.append(f"{env_prod} production")
                if env_sandbox > 0:
                    env_desc.append(f"{env_sandbox} sandbox")
                if env_dev > 0:
                    env_desc.append(f"{env_dev} developer")
                env_types = ", ".join(env_desc) if env_desc else ("1 environment" if env_count == 1 else f"{env_count} environments")
                
                if user_count > 200:
                    # Build dynamic observation and recommendation
                    obs_parts = [f"{user_count} users", env_types]
                    if flows_total > 0:
                        obs_parts.append(f"{flows_total} existing flow{'s' if flows_total != 1 else ''}")
                    if enterprise_systems:
                        obs_parts.append(f"connections to {', '.join(enterprise_systems)}")
                    
                    rec_parts = []
                    rec_parts.append(f"Plan workflow-integrated agent sessions using {env_types}: 1) Build action agents triggering flows: IT helpdesk (collects details → ServiceNow ticket)")
                    if enterprise_systems:
                        rec_parts.append(f"{enterprise_systems[0]} integration (agent gathers data → {enterprise_systems[0]} flow creates records)")
                    if suspended_flows > 0:
                        rec_parts.append(f"2) Reactivate {suspended_flows} suspended flow{'s' if suspended_flows != 1 else ''} with agent triggers")
                    
                    # Add environment guidance
                    if env_prod > 0:
                        rec_parts.append("Use dev/sandbox for flow testing, production for live integration")
                    else:
                        rec_parts.append("Test flow patterns, plan production for live workflows")
                    
                    # Add foundation context if flows exist
                    if flows_total > 0:
                        rec_parts.append(f"{flows_total} existing flows provide automation foundation")
                    
                    rec_parts.append("Target: 3 flow-integrated agents within 60 days")
                    
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Automation Session Planning",
                        observation=f"Organization ready for workflow-driven agents: {', '.join(obs_parts)}",
                        recommendation=". ".join(rec_parts) + ".",
                        link_text="Agent Flow Automation",
                        link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
                        priority="High",
                        status="Success"
                    )
                else:
                    # Build observation with flow context
                    flows_total = deployment.get('flows_total', 0)
                    suspended_flows = deployment.get('suspended_flows', 0)
                    has_servicenow = deployment.get('has_servicenow', False)
                    has_salesforce = deployment.get('has_salesforce', False)
                    
                    obs_flow_parts = [f"{user_count} users", env_types]
                    if flows_total > 0:
                        obs_flow_parts.append(f"{flows_total} flow{'s' if flows_total != 1 else ''} (workflow automation ready)")
                        if suspended_flows > 0:
                            obs_flow_parts.append(f"{suspended_flows} suspended (reactivation opportunity)")
                    else:
                        obs_flow_parts.append("no flows deployed yet (opportunity: build workflows for agent-triggered automation)")
                    
                    if has_servicenow or has_salesforce:
                        systems = [s for s, has in [('ServiceNow', has_servicenow), ('Salesforce', has_salesforce)] if has]
                        obs_flow_parts.append(f"connected to {', '.join(systems)} (flow integration ready)")
                    
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Flow-Integrated Sessions",
                        observation=f"Action agent infrastructure: {', '.join(obs_flow_parts)} - agents can trigger automated business processes",
                        recommendation=f"Build workflow-driven agents using {env_types}: 1) Create agents triggering Power Automate flows (ticket creation, approvals, data updates), 2) {'Use dev/sandbox for flow development, production for user-facing automation' if env_prod > 0 else 'Develop flow integration in current environments'}, 3) Track: sessions executing flows, flow success rates, automation time savings. Flow USL sessions complete tasks via automation. Target: 2 flow-integrated agents within 45 days.",
                        link_text="Agent Workflows",
                        link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
                        priority="Medium",
                        status="Success"
                    )
            else:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Workflow Planning",
                    observation="Flow agent sessions available for automation",
                    recommendation="Plan workflow-integrated agents: Identify action scenarios (ticket creation, approvals, system updates), build agents triggering Power Automate flows, track automation execution. Request Power Platform admin for flow management.",
                    link_text="Agent Automation",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
                    priority="Medium",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Automation Sessions",
                observation="Flow agent sessions available",
                recommendation="Build action-oriented agents: Create agents that execute Power Automate workflows to complete business tasks beyond conversation.",
                link_text="Flow Integration",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
