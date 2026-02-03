"""
Power Automate for Office 365 (Plan 3) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(pp_insights):
    """
    Check Power Automate flow deployment and integration opportunities.
    
    Args:
        pp_insights: Pre-computed Power Platform insights dict
        
    Returns:
        dict with deployment status information including flow inventory
    """
    if not pp_insights:
        return {
            'available': False,
            'error': 'no_access',
            'message': 'Power Automate flow inventory requires Power Platform Administrator access'
        }
    
    try:
        total_flows = pp_insights.get('flows_total', 0)
        cloud_flows = pp_insights.get('cloud_flows', 0)
        desktop_flows = pp_insights.get('desktop_flows', 0)
        http_triggers = pp_insights.get('http_triggers', 0)
        suspended = pp_insights.get('suspended_flows', 0)
        
        return {
            'available': True,
            'total_flows': total_flows,
            'cloud_flows': cloud_flows,
            'desktop_flows': desktop_flows,
            'http_trigger_flows': http_triggers,
            'suspended_flows': suspended,
            'copilot_plugin_candidates': http_triggers,
            'message': f'Found {total_flows} flow(s): {cloud_flows} cloud, {desktop_flows} desktop, {http_triggers} with HTTP triggers (Copilot plugin candidates)'
        }
        
    except Exception as e:
        return {
            'available': False,
            'error': 'exception',
            'message': f'Unable to check flow deployment: {str(e)}'
        }

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Automate Plan 3 enables premium connectors and RPA capabilities
    essential for extending Copilot and building enterprise agent workflows.
    Returns 2 recommendations: license status + integration opportunities status.
    """
    feature_name = "Power Automate for Office 365 (Plan 3)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling automated workflows triggered by Copilot and agents",
            recommendation="",
            link_text="Build Agent Workflows with Power Automate",
            link_url="https://learn.microsoft.com/power-automate/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting agent automation and Copilot extensibility",
            recommendation=f"Enable {feature_name} to build sophisticated agent workflows that extend M365 Copilot capabilities. Create custom actions that Copilot can trigger through prompts, automate approval processes for AI-generated content, integrate Copilot with line-of-business systems using premium connectors, and leverage RPA to have agents interact with legacy applications. Power Automate is the foundation for enterprise agent development beyond simple prompting.",
            link_text="Build Agent Workflows with Power Automate",
            link_url="https://learn.microsoft.com/power-automate/",
            priority="High",
            status=status
        )
    
    # Second recommendation: Integration opportunities (only if license is active)
    if status == "Success":
        deployment = await get_deployment_status(pp_insights)
        
        if deployment.get('available'):
            # Power Platform access available - show actual deployment status
            total_flows = deployment.get('total_flows', 0)
            http_triggers = deployment.get('http_trigger_flows', 0)
            suspended = deployment.get('suspended_flows', 0)
            cloud_flows = deployment.get('cloud_flows', 0)
            desktop_flows = deployment.get('desktop_flows', 0)
            
            # Generate specific recommendations based on actual data
            if total_flows == 0:
                # No flows yet - guide initial deployment
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Get Started",
                    observation="No Power Automate flows deployed yet - greenfield opportunity for Copilot-integrated automation",
                    recommendation="Build your first Copilot-triggered flows: 1) Start with 3-5 high-value scenarios (HR onboarding approval, CRM data lookup, report generation), 2) Create flows with HTTP triggers for Copilot plugin integration, 3) Use premium connectors to integrate SAP/Salesforce/ServiceNow, 4) Implement approval workflows for AI-generated content, 5) Deploy to default environment first, then promote to production. Target: 5 production Copilot plugins within 90 days.",
                    link_text="Build Your First Copilot Plugin with Power Automate",
                    link_url="https://learn.microsoft.com/power-automate/copilot-overview",
                    priority="High",
                    status="Success"
                )
            elif http_triggers == 0:
                # Has flows but none with HTTP triggers - conversion opportunity
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Copilot Plugin Opportunity",
                    observation=f"You have {total_flows} Power Automate flow(s) ({cloud_flows} cloud, {desktop_flows} desktop) but ZERO with HTTP triggers - missing Copilot extensibility opportunity",
                    recommendation=f"Convert {min(5, total_flows)} existing high-value flows to Copilot plugins by adding HTTP Request triggers: 1) Review your {cloud_flows} cloud flows and identify candidates (approval workflows, data retrieval, notifications), 2) Add HTTP trigger with JSON schema for Copilot parameters, 3) Register as plugins in Copilot Studio, 4) Test with natural language prompts. Priority flows: those accessing premium connectors, approval processes, or CRM/ERP data. This enables users to trigger automation via conversational prompts instead of manual execution.",
                    link_text="Convert Flows to Copilot Plugins",
                    link_url="https://learn.microsoft.com/power-automate/copilot-designer-overview",
                    priority="High",
                    status="Success"
                )
            else:
                # Has HTTP trigger flows - optimization opportunity
                plugin_percentage = int((http_triggers / total_flows) * 100) if total_flows > 0 else 0
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Expand Plugin Coverage",
                    observation=f"You have {total_flows} flow(s) with {http_triggers} Copilot plugin candidate(s) ({plugin_percentage}% plugin-ready). {suspended} flow(s) suspended/stopped requiring attention.",
                    recommendation=f"Expand Copilot plugin coverage: 1) Convert {min(3, cloud_flows - http_triggers)} more flows to plugins (target high-value business processes), 2) Fix {suspended} suspended flow(s) to restore automation, 3) Document existing {http_triggers} plugin(s) for end-user discovery, 4) Add error handling and logging to plugin flows, 5) Create flow templates for common plugin patterns. Also leverage {desktop_flows} desktop flow(s) for legacy system integration via RPA triggered by Copilot.",
                    link_text="Power Automate Plugin Best Practices",
                    link_url="https://learn.microsoft.com/power-automate/guidance/planning/process-automation",
                    priority="Medium",
                    status="Success"
                )
        else:
            # No Power Platform access - provide manual guidance
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Integration Opportunities",
                observation="Power Automate integration opportunities cannot be verified - requires Power Platform Administrator access",
                recommendation="Request Power Platform Administrator role to assess deployment opportunities, or manually review in Power Platform admin center (admin.powerplatform.microsoft.com): 1) Identify workflows that can be triggered by Copilot prompts, 2) Map premium connectors needed for Copilot extensibility (SAP, Salesforce, ServiceNow, SQL Server), 3) Design custom plugins for line-of-business systems, 4) Create RPA flows for legacy apps. Priority scenarios: HR onboarding, customer data lookup, automated reports, approval routing. Target 5-10 high-value integrations in first 90 days.",
                link_text="Copilot Extensibility with Power Automate",
                link_url="https://learn.microsoft.com/power-automate/copilot-overview",
                priority="Medium",
                status="Success"
            )
        
        return [license_rec, deployment_rec]
    
    # If license not active or no client, return only license recommendation
    return [license_rec]
