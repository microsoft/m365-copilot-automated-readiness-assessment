"""
Copilot Studio in Microsoft 365 Copilot - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name
from get_power_platform_client import extract_pp_insights_from_client

async def get_deployment_status(client, pp_insights=None):
    """
    Check for Copilot Studio agents deployment in Power Platform environments.
    Also checks M365 Copilot readiness and knowledge sources.
    
    Args:
        client: Microsoft Graph client
        pp_insights: Pre-computed Power Platform insights (optional)
    """
    try:
        import asyncio
        
        result = {
            'available': True,
            'knowledge_sources': 0,
            'has_graph_connectors': False,
            'connector_count': 0,
            'has_copilot_users': False,
            'ready_for_agents': False,
            'environments': 0,
            'has_pp_access': False
        }
        
        # Check Graph API sources and Power Platform in parallel
        tasks = [
            client.sites.get(),
            client.external.connections.get(),
            client.users.get()
        ]
        
        # Use cached Power Platform environment data if available
        if pp_insights:
            result['has_pp_access'] = True
            result['environments'] = pp_insights.get('environments_total', 0)
            result['env_production'] = pp_insights.get('production_envs', 0)
            result['env_sandbox'] = pp_insights.get('sandbox_envs', 0)
            result['env_developer'] = 0  # Not in standard pp_insights
            result['env_default'] = 0  # Not in standard pp_insights
        
        sites, connectors, users = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check SharePoint sites
        if not isinstance(sites, Exception) and sites and sites.value:
            result['knowledge_sources'] = len(sites.value)
        
        # Check Graph Connectors (enterprise knowledge)
        if not isinstance(connectors, Exception) and connectors and connectors.value:
            result['has_graph_connectors'] = True
            result['connector_count'] = len(connectors.value)
            result['knowledge_sources'] += result['connector_count']
        
        # Check for M365 Copilot users
        if not isinstance(users, Exception) and users and users.value:
            copilot_skus = ['c28afa23-5a37-4837-938f-7cc48d0cca5c', 'f2b5e97e-f677-4bb5-8127-5c3ce7b6a64e']
            for user in users.value:
                if user.assigned_licenses:
                    for license in user.assigned_licenses:
                        if license.sku_id and str(license.sku_id).lower() in [s.lower() for s in copilot_skus]:
                            result['has_copilot_users'] = True
                            break
                if result['has_copilot_users']:
                    break
        
        result['ready_for_agents'] = result['knowledge_sources'] > 0 or result['environments'] > 0
        return result
            
    except Exception as e:
        error_msg = str(e).lower()
        if '401' in error_msg or '403' in error_msg:
            return {
                'available': False,
                'error': 'insufficient_permissions',
                'message': 'Sites.Read.All and ExternalConnection.Read.All permissions required'
            }
        return {
            'available': False,
            'error': 'unknown',
            'message': f'Unable to check knowledge sources: {str(e)}'
        }

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None):
    """
    Copilot Studio in M365 Copilot enables building custom declarative agents
    that extend Copilot with organization-specific knowledge and actions.
    Returns 2 recommendations: license status + agent creation guidance.
    """
    feature_name = "Copilot Studio in Microsoft 365 Copilot"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling custom agent development within M365 Copilot",
            recommendation="",
            link_text="Build Custom Agents in Copilot Studio",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing custom agent creation for M365 Copilot",
            recommendation=f"Enable {feature_name} to unlock custom agent development capabilities within M365 Copilot. Build declarative agents specialized for specific business functions (HR, IT helpdesk, sales), connect agents to proprietary knowledge bases and SharePoint sites, define custom actions that agents can perform, and publish agents to your organization's Copilot catalog. This transforms Copilot from a general assistant into a platform for deploying specialized AI agents tailored to your business processes.",
            link_text="Build Custom Agents in Copilot Studio",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            priority="High",
            status=status
        )
    
    # Second recommendation: Agent creation readiness (only if license is active)
    if status == "Success":
        # Extract insights from pp_client if available
        pp_insights = extract_pp_insights_from_client(pp_client) if pp_client else None
        deployment = await get_deployment_status(client, pp_insights)
        
        if deployment.get('available') and deployment.get('ready_for_agents'):
            knowledge_count = deployment.get('knowledge_sources', 0)
            has_connectors = deployment.get('has_graph_connectors', False)
            connector_count = deployment.get('connector_count', 0)
            has_copilot = deployment.get('has_copilot_users', False)
            env_count = deployment.get('environments', 0)
            has_pp = deployment.get('has_pp_access', False)
            env_prod = deployment.get('env_production', 0)
            env_sandbox = deployment.get('env_sandbox', 0)
            env_dev = deployment.get('env_developer', 0)
            env_default = deployment.get('env_default', 0)
            
            if has_pp and env_count > 0:
                # Build environment description for recommendations
                env_desc = []
                if env_prod > 0:
                    env_desc.append(f"{env_prod} production")
                if env_sandbox > 0:
                    env_desc.append(f"{env_sandbox} sandbox")
                if env_dev > 0:
                    env_desc.append(f"{env_dev} developer")
                if env_default > 0:
                    env_desc.append(f"{env_default} default")
                env_types = ", ".join(env_desc) if env_desc else ("1 environment" if env_count == 1 else f"{env_count} environments")
                
                # Power Platform access available - show environment-specific guidance
                http_flow_count = len(deployment.get('http_flows', []))
                flows_total = deployment.get('flows_total', 0)
                apps_total = deployment.get('apps_total', 0)
                teams_apps = deployment.get('teams_apps', 0)
                premium_conns = deployment.get('premium_connectors', [])
                has_sap = deployment.get('has_sap', False)
                has_salesforce = deployment.get('has_salesforce', False)
                has_servicenow = deployment.get('has_servicenow', False)
                custom_conns = deployment.get('custom_connectors', [])
                ai_models = deployment.get('ai_models_total', 0)
                
                # Build Power Platform infrastructure description
                pp_desc_parts = []
                if flows_total > 0:
                    pp_desc_parts.append(f"{flows_total} flow{'s' if flows_total != 1 else ''}")
                if http_flow_count > 0:
                    pp_desc_parts.append(f"{http_flow_count} HTTP-triggered (plugin candidates)")
                if apps_total > 0:
                    pp_desc_parts.append(f"{apps_total} app{'s' if apps_total != 1 else ''}")
                if teams_apps > 0:
                    pp_desc_parts.append(f"{teams_apps} Teams-integrated")
                enterprise_systems = [s for s, has in [('SAP', has_sap), ('Salesforce', has_salesforce), ('ServiceNow', has_servicenow)] if has]
                if enterprise_systems:
                    pp_desc_parts.append(f"connections to {', '.join(enterprise_systems)}")
                if len(custom_conns) > 0:
                    pp_desc_parts.append(f"{len(custom_conns)} custom connector{'s' if len(custom_conns) != 1 else ''}")
                if ai_models > 0:
                    pp_desc_parts.append(f"{ai_models} AI model{'s' if ai_models != 1 else ''}")
                
                pp_infrastructure = ", ".join(pp_desc_parts) if pp_desc_parts else "Power Platform infrastructure available"
                
                if has_connectors and has_copilot:
                    # Build plugin conversion guidance
                    plugin_guidance = ""
                    if http_flow_count > 0:
                        plugin_guidance = f"PRIORITY: Convert {http_flow_count} HTTP-triggered flow{'s' if http_flow_count != 1 else ''} to M365 Copilot plugin{'s' if http_flow_count != 1 else ''} (seamless Copilot integration for existing automation). "
                    
                    # Build recommendation text parts
                    rec_parts = [
                        f"{plugin_guidance}Deploy declarative agents using environment-based lifecycle ({env_types}): 1) {'Use production environment for user-facing agents, sandbox/dev for testing' if env_prod > 0 else 'Promote one environment to production type for org-wide agent deployment'}",
                        "2) Build agents querying both SharePoint AND Graph Connectors for comprehensive enterprise knowledge",
                        "3) Create specialized agents: customer insights (CRM connector), compliance assistant (policy connector), product support (documentation connector)"
                    ]
                    
                    step_num = 4
                    if ai_models > 0:
                        rec_parts.append(f"{step_num}) Enhance agents with {ai_models} existing AI Builder model{'s' if ai_models != 1 else ''} for intelligent responses")
                        step_num += 1
                    if teams_apps > 0:
                        rec_parts.append(f"{step_num}) Leverage {teams_apps} Teams app{'s' if teams_apps != 1 else ''} by adding conversational layer")
                        step_num += 1
                    if enterprise_systems:
                        rec_parts.append(f"{step_num}) Build data agents using existing {', '.join(enterprise_systems)} connector{'s' if len(enterprise_systems) != 1 else ''}")
                        step_num += 1
                    
                    rec_parts.append(f"{step_num}) Enable M365 Copilot users to invoke via @AgentName from Copilot chat")
                    step_num += 1
                    
                    if env_prod > 0 and (env_sandbox > 0 or env_dev > 0):
                        rec_parts.append(f"{step_num}) Establish clear promotion path: dev → sandbox → production")
                    else:
                        rec_parts.append(f"{step_num}) Create sandbox environment for agent testing before production release")
                    
                    rec_parts.append("Deploy 2-3 pilot agents to production within 30 days, scale to 10+ agents within 90 days.")
                    
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Declarative Agent Deployment",
                        observation=f"Enterprise agent infrastructure ready: {env_types}, {knowledge_count} knowledge sources ({connector_count} Graph Connectors), M365 Copilot users deployed. Power Platform: {pp_infrastructure}",
                        recommendation=", ".join(rec_parts),
                        link_text="Deploy Declarative Agents",
                        link_url="https://learn.microsoft.com/microsoft-copilot-studio/microsoft-copilot-extend-copilot-extensions",
                        priority="High",
                        status="Success"
                    )
                elif has_connectors:
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Knowledge-Enhanced Agents",
                        observation=f"Agent infrastructure ready: {env_types}, {connector_count} Graph Connectors for enterprise knowledge integration",
                        recommendation=f"Build knowledge-enhanced declarative agents across {env_types}: 1) {'Use dev/sandbox for connector integration testing, production for deployed agents' if env_prod > 0 else 'Test connector patterns in current environments, plan production environment for enterprise rollout'}, 2) Create agents leveraging Graph Connectors to access external systems (ServiceNow, Salesforce, file shares), 3) Design department-specific agents with connector-enhanced knowledge, 4) Encourage M365 Copilot adoption to enable agent invocation. Target: 3 connector-integrated agents in production within 60 days.",
                        link_text="Agents with Graph Connectors",
                        link_url="https://learn.microsoft.com/microsoft-copilot-studio/nlu-generative-answers-sharepoint-onedrive",
                        priority="High",
                        status="Success"
                    )
                else:
                    sites_desc = f"{knowledge_count} SharePoint {'site' if knowledge_count == 1 else 'sites'}" if knowledge_count > 0 else "SharePoint sites"
                    agent_knowledge = f"Connect agents to {sites_desc} for knowledge grounding" if knowledge_count > 0 else "Connect agents to SharePoint sites for knowledge grounding (add sites to expand agent knowledge base)"
                    
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Environment-Based Agent Development",
                        observation=f"Power Platform infrastructure: {env_types}, {sites_desc} as knowledge sources",
                        recommendation=f"Leverage {env_types} for agent lifecycle management: 1) {'Use dev/sandbox for prototyping, production for org-wide deployment' if env_prod > 0 else 'Designate one environment for production agents, use others for development/testing'}, 2) Create declarative agents for high-value scenarios (HR FAQ, IT helpdesk, department knowledge), 3) {agent_knowledge}, 4) {'Establish promotion process: dev → sandbox → production with approval gates' if env_prod > 0 and env_sandbox > 0 else 'Set up environment governance before scaling agent deployment'}. Target: 2 pilot agents in {'dev' if env_dev > 0 else 'non-production'} within 30 days, promote 1 to production within 60 days.",
                        link_text="Multi-Environment Agent Strategy",
                        link_url="https://learn.microsoft.com/power-platform/admin/environments-overview",
                        priority="Medium",
                        status="Success"
                    )
            elif has_connectors and has_copilot:
                # No PP access but has connectors and Copilot
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Enterprise Agent Integration",
                    observation=f"Organization has {knowledge_count} knowledge sources ({connector_count} Graph Connectors) and M365 Copilot users - ready for enterprise-grade declarative agents",
                    recommendation=f"Build enterprise declarative agents leveraging Graph Connectors: 1) Create agents that search across indexed external systems (ServiceNow, Salesforce, file shares), 2) Design knowledge-intensive agents: product support, customer insights, compliance assistant, 3) Enable M365 Copilot users to invoke specialized agents via @mentions, 4) Request Power Platform Administrator access to manage agent deployment across multiple environments and monitor detailed usage analytics. Graph Connectors transform agents from SharePoint-only to enterprise-wide knowledge assistants.",
                    link_text="Agents with Graph Connectors",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/nlu-generative-answers-sharepoint-onedrive",
                    priority="High",
                    status="Success"
                )
            elif has_connectors:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Knowledge Integration",
                    observation=f"Organization has {connector_count} Graph Connectors providing access to enterprise knowledge sources",
                    recommendation=f"Build agents that leverage {connector_count} Graph Connectors for enterprise knowledge: Connect agents to indexed external systems, create specialized assistants for data across ServiceNow, file shares, documentation systems. Consider M365 Copilot licenses to enable users to invoke knowledge-rich agents from within Copilot.",
                    link_text="Graph Connector Integration",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/nlu-generative-answers-sharepoint-onedrive",
                    priority="Medium",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Agent Creation",
                    observation=f"Organization has {knowledge_count} SharePoint sites available as knowledge sources for custom agents",
                    recommendation=f"Start building custom declarative agents: 1) Identify 3-5 high-value use cases (HR policy assistant, IT support agent, sales enablement), 2) Create agents using existing SharePoint content, 3) Define agent instructions and actions, 4) Test with pilot users, 5) Publish to Teams and M365 Copilot. Consider deploying Graph Connectors to expand agent knowledge beyond SharePoint. Target: 3 production agents within 90 days.",
                    link_text="Create Declarative Agents",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/microsoft-copilot-extend-copilot-extensions",
                    priority="Medium",
                    status="Success"
                )
        elif deployment.get('available'):
            # No knowledge sources found
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Agent Creation",
                observation="No SharePoint sites detected - limited knowledge sources for custom agents",
                recommendation="Build organizational knowledge sources to enable custom agent creation: 1) Create SharePoint sites for department-specific content (HR policies, IT documentation, sales playbooks), 2) Migrate existing knowledge from file shares and wikis to SharePoint, 3) Structure content with metadata and search-friendly pages, 4) Grant appropriate permissions for agent access. Custom agents need quality knowledge sources to provide accurate responses. Without SharePoint content, agents will have limited value. Priority: Establish at least 3 knowledge repositories (HR, IT, one business unit) before creating agents.",
                link_text="Prepare Knowledge Sources",
                link_url="https://learn.microsoft.com/sharepoint/introduction",
                priority="High",
                status="Success"
            )
        else:
            # Cannot verify
            error_msg = deployment.get('message', 'Unable to verify knowledge source readiness')
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Agent Creation",
                observation=f"Custom agent readiness could not be verified ({error_msg})",
                recommendation="Manually assess custom agent creation readiness: 1) Verify SharePoint sites with structured content for agent knowledge sources, 2) Identify business processes suitable for agent automation (FAQ answering, data lookup, guided workflows), 3) Select 3-5 pilot use cases with clear success metrics, 4) Assign agent owners from business units who understand domain content, 5) Plan 30-day pilot with 10-20 users per agent. Access Copilot Studio portal to create first declarative agent using low-code builder.",
                link_text="Copilot Studio Portal",
                link_url="https://copilotstudio.microsoft.com/",
                priority="Medium",
                status="Success"
            )
        
        return [license_rec, deployment_rec]
    
    # If license not active or no client, return only license recommendation
    return [license_rec]
