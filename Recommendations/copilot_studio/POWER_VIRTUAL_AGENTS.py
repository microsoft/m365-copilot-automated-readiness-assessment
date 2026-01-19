"""
Power Virtual Agents - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name
from get_power_platform_client import extract_pp_insights_from_client

async def get_deployment_status(client, pp_insights=None):
    """
    Check Power Virtual Agents (Copilot Studio) agent deployment infrastructure.
    Queries Power Platform environments, M365 Copilot licenses, and SharePoint sites.
    """
    try:
        import asyncio
        
        result = {
            'available': True,
            'has_users': False,
            'has_copilot_users': False,
            'has_knowledge_sources': False,
            'user_count': 0,
            'copilot_count': 0,
            'site_count': 0,
            'environments': 0,
            'has_pp_access': False
        }
        
        # Prepare tasks for parallel execution
        tasks = [client.users.get(), client.sites.get()]
        
        # Use pre-computed Power Platform insights
        if pp_insights:
            result['has_pp_access'] = True
            result['environments'] = pp_insights.get('environments_total', 0)
            result['env_production'] = pp_insights.get('production_envs', 0)
            result['env_sandbox'] = pp_insights.get('sandbox_envs', 0)
            result['env_developer'] = 0  # Not in standard pp_insights
            result['flows_total'] = pp_insights.get('flows_total', 0)
            result['http_flows'] = pp_insights.get('http_triggers', 0)
            result['apps_total'] = pp_insights.get('apps_total', 0)
            result['teams_apps'] = pp_insights.get('teams_apps', 0)
            result['premium_connectors'] = pp_insights.get('premium_connectors', 0)
        
        users, sites = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for M365 Copilot license assignments
        if not isinstance(users, Exception) and users and users.value:
            result['has_users'] = True
            result['user_count'] = len(users.value)
            
            copilot_skus = [
                'c28afa23-5a37-4837-938f-7cc48d0cca5c',  # M365 Copilot
                'f2b5e97e-f677-4bb5-8127-5c3ce7b6a64e'   # M365 Copilot (additional SKU)
            ]
            
            copilot_users = 0
            for user in users.value:
                if user.assigned_licenses:
                    for license in user.assigned_licenses:
                        if license.sku_id and str(license.sku_id).lower() in [s.lower() for s in copilot_skus]:
                            copilot_users += 1
                            break
            
            result['copilot_count'] = copilot_users
            result['has_copilot_users'] = copilot_users > 0
        
        # Check SharePoint sites (knowledge sources for agents)
        if not isinstance(sites, Exception) and sites and sites.value:
            result['has_knowledge_sources'] = True
            result['site_count'] = len(sites.value)
        
        return result
        
    except Exception as e:
        return {
            'available': False,
            'error': 'unknown',
            'message': f'Unable to check agent deployment infrastructure: {str(e)}'
        }

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Virtual Agents (now Copilot Studio) - conversational agent capabilities.
    Returns 2 recommendations: license status + agent deployment strategy based on PP infrastructure.
    """
    feature_name = "Power Virtual Agents"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing agent creation capabilities (now part of Copilot Studio)",
            recommendation="",
            link_text="Copilot Studio (formerly PVA)",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing conversational AI agent creation platform",
            recommendation=f"Enable {feature_name} (now Copilot Studio) to build custom conversational agents for employee and customer scenarios. Create agents that answer common questions, automate repetitive tasks, gather information through natural language, and integrate with business systems. Power Virtual Agents has evolved into Copilot Studio, which extends M365 Copilot with custom agents tailored to organizational processes. Essential for HR support agents, IT helpdesk automation, customer service bots, and specialized knowledge assistants that complement M365 Copilot's general productivity features.",
            link_text="Copilot Studio (formerly PVA)",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            priority="Medium",
            status=status
        )
    
    # Second recommendation: Agent deployment strategy (only if license is active)
    if status == "Success" and client:
        # Extract insights from pp_client if available
        pp_insights = extract_pp_insights_from_client(pp_client) if pp_client else None
        deployment = await get_deployment_status(client, pp_insights)
        
        if deployment.get('available'):
            has_copilot = deployment.get('has_copilot_users', False)
            copilot_count = deployment.get('copilot_count', 0)
            has_knowledge = deployment.get('has_knowledge_sources', False)
            site_count = deployment.get('site_count', 0)
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
                
                # Build PP infrastructure description
                flows_total = deployment.get('flows_total', 0)
                http_flows = deployment.get('http_flows', 0)
                apps_total = deployment.get('apps_total', 0)
                teams_apps = deployment.get('teams_apps', 0)
                premium_conns = deployment.get('premium_connectors', 0)
                
                pp_assets = []
                if flows_total > 0:
                    pp_assets.append(f"{flows_total} flow{'s' if flows_total != 1 else ''}")
                    if http_flows > 0:
                        pp_assets.append(f"{http_flows} HTTP-triggered (convert to M365 Copilot plugins)")
                else:
                    pp_assets.append("no flows yet (build automation for agent actions)")
                
                if apps_total > 0:
                    pp_assets.append(f"{apps_total} app{'s' if apps_total != 1 else ''}")
                    if teams_apps > 0:
                        pp_assets.append(f"{teams_apps} Teams-integrated")
                else:
                    pp_assets.append("no apps yet (opportunity: build canvas/model-driven apps with conversational layer)")
                
                if premium_conns > 0:
                    pp_assets.append(f"{premium_conns} premium connector{'s' if premium_conns != 1 else ''} (enterprise integrations)")
                else:
                    pp_assets.append("no premium connectors yet (connect to SAP/Salesforce/ServiceNow for data agents)")
                
                pp_infrastructure = f", Power Platform: {', '.join(pp_assets)}"
                
                # Power Platform access - environment-specific agent deployment strategy
                if has_copilot and has_knowledge:
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Enterprise Agent Deployment",
                        observation=f"Enterprise agent infrastructure: {env_types}, {copilot_count} M365 Copilot users, {site_count} SharePoint knowledge sources{pp_infrastructure}",
                        recommendation=f"Deploy enterprise conversational agent strategy using {env_types}: 1) Build specialized support agents: IT helpdesk (password resets, software requests), HR assistant (PTO policies, benefits), facilities (room booking, maintenance), 2) Connect to {site_count} SharePoint sites for knowledge-grounded responses, 3) {'Use dev/sandbox for agent testing, production for org-wide deployment' if env_prod > 0 else 'Establish production environment for enterprise agent rollout, use current for testing'}, 4) Enable M365 Copilot integration ({copilot_count} users can invoke agents via @ITAgent, @HRAgent), 5) Implement handoff-to-human for complex cases, 6) {'Establish promotion workflow: dev → sandbox → production' if env_prod and (env_sandbox or env_dev) else 'Set up environment governance for agent lifecycle'}. Track: deflection rate, user satisfaction. Target: 3 production agents within 60 days, 40% deflection within 90 days.",
                        link_text="Deploy Enterprise Agents",
                        link_url="https://learn.microsoft.com/microsoft-copilot-studio/publication-fundamentals-publish-channels",
                        priority="High",
                        status="Success"
                    )
                elif has_knowledge:
                    # Build observation for knowledge agents with PP infrastructure
                    kb_obs_parts = [env_types, f"{site_count} SharePoint site{'s' if site_count != 1 else ''} (knowledge sources)"]
                    if pp_assets:
                        kb_obs_parts.append(f"Power Platform: {', '.join(pp_assets)}")
                    
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Knowledge Agent Development",
                        observation=f"Knowledge-driven agent infrastructure: {', '.join(kb_obs_parts)}",
                        recommendation=f"Build knowledge-driven conversational agents using {env_types}: 1) Create agents answering questions from {site_count} SharePoint sites (policies, procedures, documentation), 2) Leverage generative answers to pull context from SharePoint automatically, 3) Deploy to high-volume departments (IT, HR, compliance), 4) {'Use dev/sandbox for pilot testing, production for org-wide Teams deployment' if env_prod > 0 else 'Test in current environments, plan production setup for enterprise rollout'}, 5) Monitor analytics: common questions, knowledge gaps, confidence scores. Consider M365 Copilot to enable agent invocation as specialized assistants. Target: 2-3 knowledge agents in production within 45 days, 30% deflection.",
                        link_text="Knowledge-Driven Agents",
                        link_url="https://learn.microsoft.com/microsoft-copilot-studio/nlu-boost-conversations",
                        priority="Medium",
                        status="Success"
                    )
                else:
                    deployment_rec = new_recommendation(
                        service="Copilot Studio",
                        feature=f"{feature_name} - Agent Infrastructure Planning",
                        observation=f"Agent development infrastructure: {env_types} for agent lifecycle management",
                        recommendation=f"Establish agent workflow using {env_types}: 1) {'Use dev/sandbox for creation/testing, production for org-wide deployment' if env_prod > 0 else 'Set up production environment for enterprise agents, use current for development'}, 2) Identify initial scenarios: high-volume tasks (password resets, time-off, troubleshooting), 3) Build SharePoint knowledge repositories before agent creation, 4) {'Implement dev → sandbox → production promotion workflow' if env_prod and (env_sandbox or env_dev) else 'Establish environment governance and promotion process'}. Priority: Create SharePoint content as agent knowledge foundation. Target: First pilot agent within 45 days.",
                        link_text="Bot Development Lifecycle",
                        link_url="https://learn.microsoft.com/power-platform/admin/environments-overview",
                        priority="Medium",
                        status="Success"
                    )
            elif has_copilot and has_knowledge:
                # No PP access - focus on M365 Copilot agent integration
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - M365 Copilot Agent Integration",
                    observation=f"Organization ready for agent-extended Copilot: {copilot_count} M365 Copilot users, {site_count} SharePoint knowledge sources",
                    recommendation=f"Build conversational agents that extend M365 Copilot capabilities: 1) Create specialized agents for tasks beyond Copilot's general productivity: department-specific processes (sales methodology, engineering standards), complex policy navigation (expense rules, compliance procedures), multi-step workflows (onboarding checklist, project initiation), 2) Connect agents to {site_count} SharePoint sites for domain-specific knowledge, 3) Enable M365 Copilot users to invoke agents via @mentions in Teams/Copilot interface, 4) Design agents for delegation: M365 Copilot handles general queries, delegates specialized tasks to your agents, 5) Request Power Platform Administrator access to manage multi-environment deployment and access detailed agent analytics. Target: 2-3 specialized agents deployed within 60 days, measurable M365 Copilot user engagement.",
                    link_text="Build M365 Copilot Agents",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/copilot-conversational-plugins",
                    priority="High",
                    status="Success"
                )
            elif has_knowledge:
                # Knowledge available - build standalone agents
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Standalone Agent Deployment",
                    observation=f"Organization has {site_count} SharePoint sites available for agent knowledge sources",
                    recommendation=f"Build standalone conversational agents leveraging existing SharePoint content: 1) Identify departments with repetitive Q&A burden (IT helpdesk, HR, facilities, compliance), 2) Create agents using generative answers to pull from {site_count} SharePoint sites, 3) Deploy to Teams channels where employees already ask questions, 4) Track key metrics: deflection rate (% answered without human), response confidence scores, most common questions, 5) Iterate based on analytics: add topics for low-confidence areas, create SharePoint content for knowledge gaps. Consider M365 Copilot to enable agent invocation as specialized assistants. Target: 2 pilot agents within 45 days, measure deflection improvement month-over-month.",
                    link_text="Standalone Agent Guide",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/fundamentals-get-started",
                    priority="Medium",
                    status="Success"
                )
            else:
                # Limited readiness
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Agent Planning",
                    observation="Agent platform available - planning phase for agent deployment",
                    recommendation="Plan agent adoption roadmap: 1) Identify high-impact use cases (IT support, HR FAQ, process automation), 2) Build SharePoint knowledge repositories for agent responses, 3) Start with simple FAQ agent before complex conversational flows, 4) Deploy pilot to small group, measure success (deflection rate, user satisfaction), 5) Scale based on pilot results. Priority: Create quality SharePoint content before agent development.",
                    link_text="Agent Planning Guide",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/fundamentals-what-is-copilot-studio",
                    priority="Low",
                    status="Success"
                )
        else:
            # Cannot verify readiness
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Agent Deployment",
                observation="Agent deployment readiness cannot be automatically verified",
                recommendation="Manually verify agent deployment readiness: Check Power Platform admin center for deployed agents, review agent usage analytics, identify M365 Copilot integration opportunities. Plan initial agent scenarios and knowledge sources.",
                link_text="Copilot Studio Admin Guide",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/admin-center",
                priority="Medium",
                status="Success"
            )
        
        return [license_rec, deployment_rec]
    
    # If license not active, return only license recommendation
    return [license_rec]
