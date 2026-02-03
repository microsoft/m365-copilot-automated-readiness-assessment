"""
Project for Office 365 (Plan 1) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for project management usage and opportunities."""
    try:
        import asyncio
        users_task = client.users.get()
        groups_task = client.groups.get()
        
        users, groups = await asyncio.gather(users_task, groups_task, return_exceptions=True)
        
        result = {'available': True, 'user_count': 0, 'has_teams': False}
        if not isinstance(users, Exception) and users and users.value:
            result['user_count'] = len(users.value)
        if not isinstance(groups, Exception) and groups and groups.value:
            result['has_teams'] = len(groups.value) > 0
        return result
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None, m365_insights=None):
    """
    Project Plan 1 provides basic project management with web-based Project for the web.
    Returns list of recommendations: license status + AI-assisted project management opportunities + m365 insights.
    """
    recommendations = []
    
    feature_name = "Project for Office 365 (Plan 1)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing web-based project management with task tracking and roadmaps",
            recommendation="",
            link_text="Project for the Web",
            link_url="https://learn.microsoft.com/project-for-the-web/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing basic project management capabilities",
            recommendation=f"Enable {feature_name} (Project for the web) to provide AI-ready project management. Plan 1 includes browser-based project planning, task management with dependencies, timeline views, and roadmap visualization. Build Copilot-assisted workflows where agents help: create project plans from requirement documents, update task statuses from Teams conversations, identify blockers and suggest mitigation, generate status reports automatically. Project data stored in Dataverse enables agents to answer natural language queries about timelines, resource allocation, and project health without manual reporting.",
            link_text="Project for the Web",
            link_url="https://learn.microsoft.com/project-for-the-web/",
            priority="Low",
            status=status
        )
    recommendations.append(license_rec)
    
    # M365 Insights - AI Project Management
    if m365_insights:
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Project Plan 1 provides AI-ready project management via browser-based Project for the web. Data stored in Dataverse enables Copilot Studio agents to answer natural language queries: 'What's blocking Project Alpha?', 'Who's overallocated this week?', 'When will release milestone complete?'. Agents can create projects from requirement docs, update task statuses from Teams conversations, generate automated status reports. Eliminates manual project reporting - AI extracts insights directly from task data, dependencies, timelines. Foundation for conversational project management.",
            recommendation="",
            link_text="AI Project Management",
            link_url="https://learn.microsoft.com/project-for-the-web/",
            status="Success"
        ))
        
        # Threshold-based recommendations
        if teams_active_users >= 100:
            recommendations.append(new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"With {teams_active_users} Teams users collaborating on projects, Copilot Studio agents can automate status reporting and answer project queries",
                recommendation=f"Deploy Project Plan 1 AI scenarios for your {teams_active_users} Teams users: Build Copilot Studio agent that answers project status questions from Dataverse project data, automate task updates from Teams conversations, generate weekly status reports in natural language. Reduce manual project administration by 70% - let AI extract insights from task dependencies, timelines, resource allocation. Teams integration enables conversational project management: 'update my tasks', 'what's critical path?', 'generate status report'.",
                link_text="AI Project Deployment",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                status="Insight",
                priority="Medium"
            ))
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            user_count = deployment.get('user_count', 0)
            has_teams = deployment.get('has_teams', False)
            
            if user_count > 500 and has_teams:
                deployment_rec = new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - AI Project Assistant",
                    observation=f"Large organization ({user_count} users) with Teams collaboration - ready for AI-assisted project management",
                    recommendation="Build AI project assistant with Copilot Studio and Power Automate: 1) Create agent that answers project status questions ('What's blocking Project Alpha?', 'Who's overallocated this week?'), 2) Automate task updates from Teams messages and email, 3) Generate weekly status reports from Project data in natural language, 4) Alert stakeholders when tasks become critical path or miss milestones. Project for the web stores data in Dataverse enabling agents to query projects, tasks, and resources through conversational AI. Reduce manual status reporting by 70% while improving visibility.",
                    link_text="AI Project Management",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                    priority="High",
                    status="Success"
                )
            elif user_count > 100:
                deployment_rec = new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Project Copilot",
                    observation=f"Organization ({user_count} users) can benefit from AI-enhanced project workflows",
                    recommendation="Start with simple AI project scenarios: Create Copilot Studio agent to answer project status questions, automate task creation from Teams requests, generate progress summaries. Project data in Dataverse enables natural language queries.",
                    link_text="Project with Copilot Studio",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                    priority="Medium",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Getting Started",
                    observation="Project for the web available for team project management",
                    recommendation="Start managing projects in Project for the web: Create project plans, assign tasks with dependencies, track progress with timeline views. Leverage Dataverse integration for future AI assistant scenarios.",
                    link_text="Get Started with Project",
                    link_url="https://learn.microsoft.com/project-for-the-web/get-started-project-for-the-web",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Planning",
                observation="Project for the web ready for AI-enhanced project management",
                recommendation="Plan AI-assisted project workflows: automated status updates, natural language project queries, intelligent task routing, and predictive timeline analysis.",
                link_text="Project for the Web",
                link_url="https://learn.microsoft.com/project-for-the-web/",
                priority="Low",
                status="Success"
            )
        recommendations.append(deployment_rec)
    
    return recommendations
