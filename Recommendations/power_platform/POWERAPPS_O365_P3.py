"""
Power Apps for Office 365 (Plan 3) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client, pp_insights=None):
    """
    Check Power Apps deployment status and Copilot integration opportunities.
    """
    # Use pre-computed Power Platform insights
    if pp_insights:
        total_apps = pp_insights.get('apps_total', 0)
        canvas_apps = pp_insights.get('canvas_apps', 0)
        model_apps = pp_insights.get('model_driven_apps', 0)
        teams_apps = pp_insights.get('teams_apps', 0)
        
        return {
            'available': True,
            'total_apps': total_apps,
            'canvas_apps': canvas_apps,
            'model_driven_apps': model_apps,
            'teams_integrated': teams_apps,
            'has_apps': total_apps > 0,
            'source': 'power_platform'
        }
    
    # Fallback to Graph API for organization context
    try:
        import asyncio
        sites_task = client.sites.get()
        users_task = client.users.get()
        
        sites, users = await asyncio.gather(sites_task, users_task, return_exceptions=True)
        
        result = {'available': True, 'has_data_sources': False, 'user_count': 0, 'source': 'graph'}
        
        if not isinstance(sites, Exception) and sites and sites.value:
            result['has_data_sources'] = len(sites.value) > 0
        
        if not isinstance(users, Exception) and users and users.value:
            result['user_count'] = len(users.value)
        
        return result
    except Exception as e:
        return {'available': False, 'reason': str(e)}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Apps Plan 3 enables building custom agent interfaces.
    Returns 2 recommendations: license status + app deployment guidance.
    """
    feature_name = "Power Apps for Office 365 (Plan 3)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling custom AI-powered applications and agent interfaces",
            recommendation="",
            link_text="Build Copilot-Powered Apps with Power Apps",
            link_url="https://learn.microsoft.com/power-apps/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing custom agent UI development",
            recommendation=f"Enable {feature_name} to create custom applications powered by Copilot and agents. Build specialized interfaces where agents interact with users for specific business processes, embed Copilot capabilities into line-of-business apps, and create agent-driven forms that intelligently guide users through complex workflows. Power Apps with AI Builder integration transforms traditional apps into intelligent, conversational experiences.",
            link_text="Build Copilot-Powered Apps with Power Apps",
            link_url="https://learn.microsoft.com/power-apps/",
            priority="Medium",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client, pp_insights)
        if deployment.get('available'):
            # Check if we have actual app data from Power Platform
            if deployment.get('source') == 'power_platform':
                total_apps = deployment.get('total_apps', 0)
                canvas_apps = deployment.get('canvas_apps', 0)
                model_apps = deployment.get('model_driven_apps', 0)
                teams_apps = deployment.get('teams_integrated', 0)
                
                if total_apps == 0:
                    # No apps yet - greenfield opportunity
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - Get Started",
                        observation="No Power Apps deployed yet - opportunity to build Copilot-first app experiences from scratch",
                        recommendation="Build your first Copilot-integrated Power App: 1) Start with a simple business process (expense submission, equipment request, time-off approval), 2) Use Copilot Control to add conversational interface instead of traditional forms, 3) Connect to Dataverse for data persistence and sharing with agents, 4) Embed AI Builder for document processing or prediction, 5) Deploy to Microsoft Teams for M365 integration. Target: 2-3 pilot apps with Copilot features in first 60 days.",
                        link_text="Build Copilot-Enabled Apps",
                        link_url="https://learn.microsoft.com/power-apps/maker/canvas-apps/ai-overview",
                        priority="High",
                        status="Success"
                    )
                elif teams_apps == 0:
                    # Has apps but none in Teams - integration opportunity
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - Teams Integration",
                        observation=f"You have {total_apps} Power App(s) ({canvas_apps} canvas, {model_apps} model-driven) but ZERO integrated with Teams - missing M365 Copilot integration point",
                        recommendation=f"Integrate {min(3, total_apps)} existing Power Apps with Microsoft Teams to enable Copilot discovery and interaction: 1) Add existing apps as Teams tabs or personal apps, 2) Enable app notifications in Teams channels, 3) Create app shortcuts for quick Copilot-triggered access, 4) Use Teams context (user, channel, team) in app logic. Teams integration makes apps discoverable by M365 Copilot and enables conversational app launching via prompts like 'Open expense app'.",
                        link_text="Integrate Power Apps with Teams",
                        link_url="https://learn.microsoft.com/power-apps/teams/embed-teams-app",
                        priority="High",
                        status="Success"
                    )
                else:
                    # Has apps in Teams - optimization opportunity
                    teams_percentage = int((teams_apps / total_apps) * 100) if total_apps > 0 else 0
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - Enhance with Copilot",
                        observation=f"You have {total_apps} app(s) with {teams_apps} in Teams ({teams_percentage}% integrated). {canvas_apps} canvas apps ideal for Copilot Control embedding.",
                        recommendation=f"Enhance existing apps with Copilot capabilities: 1) Add Copilot Control to {min(3, canvas_apps)} canvas apps for conversational data entry, 2) Integrate AI Builder models (document processing, predictions) into {min(2, total_apps)} apps, 3) Create app-specific agents that guide users through complex workflows, 4) Implement voice input for mobile scenarios, 5) Build agent-driven model-driven apps that auto-populate from conversations. Prioritize high-traffic apps for maximum user impact.",
                        link_text="Copilot Control in Power Apps",
                        link_url="https://learn.microsoft.com/power-apps/maker/canvas-apps/add-ai-copilot",
                        priority="Medium",
                        status="Success"
                    )
            else:
                # Fallback to Graph-based recommendations
                user_count = deployment.get('user_count', 0)
                has_sources = deployment.get('has_data_sources', False)
                
                if has_sources and user_count > 100:
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - Copilot Integration",
                        observation=f"Large organization ({user_count} users) with data sources - ideal for Copilot-embedded apps",
                        recommendation="Build Power Apps with embedded Copilot capabilities: 1) Create canvas apps where users interact via chat instead of forms (e.g., expense submission via conversation), 2) Embed AI Builder models for document processing, sentiment analysis, form recognition, 3) Use Copilot Control to add natural language interface to existing apps, 4) Build model-driven apps that agents populate automatically, 5) Connect apps to Dataverse for agent data sharing. Deploy to Teams for seamless M365 Copilot integration.",
                        link_text="Copilot in Power Apps",
                        link_url="https://learn.microsoft.com/power-apps/maker/canvas-apps/ai-overview",
                        priority="Medium",
                        status="Success"
                    )
                elif has_sources:
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - App Development",
                        observation="Data sources available - ready for custom app development",
                        recommendation="Build first Copilot-enhanced Power App: Start with simple scenario (data entry, approval, lookup), add Copilot control for natural language interaction, test with pilot group. Power Apps makes agent interfaces tangible and user-friendly.",
                        link_text="Build Your First App",
                        link_url="https://learn.microsoft.com/power-apps/maker/canvas-apps/getting-started",
                        priority="Low",
                        status="Success"
                    )
                else:
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - Planning",
                        observation=f"Power Apps deployment data unavailable (API error) - organization with {user_count} users ready for app development",
                        recommendation="Plan Power Apps deployment: Identify processes suited for custom apps (forms, approvals, mobile data access), consider Copilot integration opportunities, start with pilot use case. Recommend reviewing Power Platform admin center for actual app inventory.",
                        link_text="Power Apps Planning",
                        link_url="https://learn.microsoft.com/power-apps/",
                        priority="Low",
                        status="Success"
                    )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Deployment",
                observation="Power Apps deployment readiness verification unavailable",
                recommendation="Assess Power Apps opportunities: Identify business processes needing custom interfaces, plan Copilot integration, evaluate AI Builder scenarios for intelligent automation.",
                link_text="Power Apps Overview",
                link_url="https://learn.microsoft.com/power-apps/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
