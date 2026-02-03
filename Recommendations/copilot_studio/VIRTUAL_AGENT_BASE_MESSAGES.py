"""
Power Virtual Agents (Base) - Copilot Studio & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """
    Check Teams activity as proxy for potential agent conversation volume.
    """
    try:
        teams_activity = await client.reports.get_teams_user_activity_counts(period='D30').get()
        
        if teams_activity and teams_activity.value:
            total_messages = 0
            for row in teams_activity.value:
                if hasattr(row, 'team_chat_messages'):
                    total_messages += int(row.team_chat_messages or 0)
            
            return {
                'available': True,
                'monthly_messages': total_messages,
                'high_volume': total_messages > 10000
            }
        else:
            return {'available': False, 'reason': 'No Teams activity data'}
            
    except Exception as e:
        error_msg = str(e).lower()
        if '401' in error_msg or '403' in error_msg:
            return {'available': False, 'reason': 'Reports.Read.All permission required'}
        return {'available': False, 'reason': f'Unable to check activity: {str(e)}'}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    Power Virtual Agents (Base) provides basic agent creation capabilities.
    Returns 2 recommendations: license status + capacity planning.
    """
    feature_name = "Power Virtual Agents (Base)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing base agent creation capabilities in Copilot Studio",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Copilot Studio",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to provide basic conversational agent creation capabilities.",
            link_text="Copilot Studio (formerly PVA)",
            link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
            priority="Medium",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        
        if deployment.get('available'):
            monthly_msgs = deployment.get('monthly_messages', 0)
            if deployment.get('high_volume'):
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Agent Planning",
                    observation=f"High Teams activity ({monthly_msgs:,} messages/month) indicates strong potential for agent automation",
                    recommendation="Plan agents for high-volume scenarios: Estimate 10-20% of repetitive conversations can be automated. Prioritize agents that deflect common questions from busy channels. Track metrics: resolution rate, time saved, user satisfaction.",
                    link_text="Agent Best Practices",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/analytics-overview",
                    priority="Medium",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Copilot Studio",
                    feature=f"{feature_name} - Agent Planning",
                    observation=f"Moderate activity ({monthly_msgs:,} messages/month) - agent message capacity sufficient for 2-3 pilot agents serving 50-100 users each",
                    recommendation="Start with 2-3 pilot agents for specific departments. Monitor adoption and impact metrics. Expand after validating agent value and user adoption patterns.",
                    link_text="Agent Deployment Guide",
                    link_url="https://learn.microsoft.com/microsoft-copilot-studio/",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Copilot Studio",
                feature=f"{feature_name} - Message Planning",
                observation="Agent message capacity allocated - enables conversational agents to handle employee questions (HR policies, IT support, facilities requests)",
                recommendation="Plan agent message usage: Estimate monthly messages (users × conversations/month × messages/conversation). Start with 2-3 pilot agents to establish baseline consumption. Monitor usage in Power Platform admin center and adjust capacity as adoption grows.",
                link_text="Message Analytics",
                link_url="https://learn.microsoft.com/microsoft-copilot-studio/analytics-overview",
                priority="Low",
                status="Success"
            )
        
        return [license_rec, deployment_rec]
    
    return [license_rec]
