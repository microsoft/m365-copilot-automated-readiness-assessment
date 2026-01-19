"""
Power BI Pro - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """Check for Power BI readiness via SharePoint and user base."""
    try:
        import asyncio
        sites_task = client.sites.get()
        users_task = client.users.get()
        
        sites, users = await asyncio.gather(sites_task, users_task, return_exceptions=True)
        
        result = {'available': True, 'has_data': False, 'user_count': 0}
        if not isinstance(sites, Exception) and sites and sites.value:
            result['has_data'] = len(sites.value) > 0
        if not isinstance(users, Exception) and users and users.value:
            result['user_count'] = len(users.value)
        return result
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power BI Pro enables AI-powered analytics.
    Returns 2 recommendations: license status + analytics opportunities.
    """
    feature_name = "Power BI Pro"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-powered business intelligence and analytics",
            recommendation="",
            link_text="AI Analytics with Power BI",
            link_url="https://learn.microsoft.com/power-bi/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting AI-driven insights and dashboard creation",
            recommendation=f"Enable {feature_name} to extend Copilot's analytics beyond Excel into enterprise dashboards. Use natural language to query Power BI datasets ('Show me sales trends by region'), let Copilot generate DAX formulas for complex calculations, and create AI-powered narratives explaining dashboard insights. Power BI agents can deliver personalized report summaries, alert stakeholders to anomalies, and answer data questions through conversational interfaces. Essential for data-driven organizations building AI into their analytics stack.",
            link_text="AI Analytics with Power BI",
            link_url="https://learn.microsoft.com/power-bi/",
            priority="Medium",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        if deployment.get('available'):
            user_count = deployment.get('user_count', 0)
            has_data = deployment.get('has_data', False)
            
            if has_data and user_count > 100:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Copilot Integration",
                    observation=f"Large organization ({user_count} users) with data sources - ready for AI-powered analytics",
                    recommendation="Build Power BI Copilot integration: 1) Create datasets from SharePoint lists, Excel files, Dataverse tables, 2) Enable natural language Q&A on reports (users ask questions in plain English), 3) Use Copilot to generate DAX measures and calculated columns, 4) Create narrative visuals that explain trends automatically, 5) Build agents that deliver daily/weekly report summaries via Teams. Target: 3-5 core dashboards with Copilot Q&A enabled within 60 days for executive/department reporting.",
                    link_text="Copilot in Power BI",
                    link_url="https://learn.microsoft.com/power-bi/create-reports/copilot-introduction",
                    priority="Medium",
                    status="Success"
                )
            elif has_data:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Analytics Start",
                    observation="Data sources available - ready for first Power BI dashboards",
                    recommendation="Build first AI-enhanced Power BI report: Connect to data source, create basic visuals, enable Q&A for natural language queries. Start with executive dashboard or department KPIs.",
                    link_text="Get Started with Power BI",
                    link_url="https://learn.microsoft.com/power-bi/fundamentals/desktop-getting-started",
                    priority="Low",
                    status="Success"
                )
            else:
                # Reference Power Platform environment data for context
                env_info = ""
                if pp_insights:
                    total_envs = pp_insights.get('environments_total', 0)
                    if total_envs > 0:
                        env_info = f" With {total_envs} Power Platform environment(s), you can embed BI insights in apps and agents."
                
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Planning",
                    observation=f"Power BI Pro enables users to ask Copilot questions about business data in natural language ('Show me sales trends') instead of building manual reports.{env_info}",
                    recommendation="Plan Power BI deployment: Identify key metrics and data sources, design dashboard strategy, consider Copilot Q&A for user-friendly analytics.",
                    link_text="Power BI Planning",
                    link_url="https://learn.microsoft.com/power-bi/",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Analytics",
                observation="Power BI Pro readiness verification unavailable",
                recommendation="Assess Power BI opportunities for AI-powered analytics: Identify reports to migrate from Excel, plan datasets, enable Copilot Q&A for conversational insights.",
                link_text="Power BI Overview",
                link_url="https://learn.microsoft.com/power-bi/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
