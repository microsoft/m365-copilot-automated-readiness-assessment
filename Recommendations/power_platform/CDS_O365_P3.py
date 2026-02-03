"""
Common Data Service for Office 365 (Plan 3) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(client, pp_client=None, pp_insights=None):
    """Check Dataverse capacity and usage for agent scalability planning."""
    # Try to use Power Platform client first for actual capacity data
    if pp_client and hasattr(pp_client, 'capacity_summary'):
        capacity = pp_client.capacity_summary
        
        # Check if we successfully fetched capacity
        if capacity.get('available'):
            db_usage = capacity.get('database_usage_percent', 0)
            file_usage = capacity.get('file_usage_percent', 0)
            db_capacity_mb = capacity.get('database_capacity_mb', 0)
            db_used_mb = capacity.get('database_used_mb', 0)
            
            return {
                'available': True,
                'database_usage_percent': db_usage,
                'file_usage_percent': file_usage,
                'database_capacity_mb': db_capacity_mb,
                'database_used_mb': db_used_mb,
                'at_capacity': db_usage >= 85,
                'high_usage': db_usage >= 70,
                'source': 'power_platform'
            }
    
    # Fallback to user count estimation
    try:
        users = await client.users.get()
        if users and users.value:
            return {'available': True, 'user_count': len(users.value), 'enterprise_scale': len(users.value) > 1000, 'source': 'graph'}
        return {'available': True, 'user_count': 0, 'enterprise_scale': False, 'source': 'graph'}
    except:
        return {'available': False}

async def get_recommendation(sku_name, status="Success", client=None, pp_client=None, pp_insights=None):
    """
    CDS Plan 3 provides premium database for enterprise agents.
    Returns 2 recommendations: license status + capacity planning.
    """
    feature_name = "Common Data Service for Office 365 (Plan 3)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing premium database capacity for enterprise agent solutions",
            recommendation="",
            link_text="Premium Dataverse for Agents",
            link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Power Platform",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing premium database platform for enterprise agents",
            recommendation=f"Enable {feature_name} (Dataverse for Office 365 Plan 3) to provide maximum database capacity for enterprise-scale agent deployments. Plan 3 supports agents serving thousands of users, managing extensive business data, and integrating with complex enterprise systems. Build agents that handle high conversation volumes, maintain comprehensive audit trails, and access large datasets for contextual responses. Essential for organization-wide agent deployments where database capacity directly impacts user experience and agent capabilities.",
            link_text="Premium Dataverse for Agents",
            link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
            priority="Low",
            status=status
        )
    
    if status == "Success" and client:
        deployment = await get_deployment_status(client, pp_client)
        if deployment.get('available'):
            # Check if we have actual capacity data
            if deployment.get('source') == 'power_platform':
                db_usage = deployment.get('database_usage_percent', 0)
                db_capacity_mb = deployment.get('database_capacity_mb', 0)
                db_used_mb = deployment.get('database_used_mb', 0)
                at_capacity = deployment.get('at_capacity', False)
                high_usage = deployment.get('high_usage', False)
                
                # Calculate remaining capacity in GB
                remaining_gb = (db_capacity_mb - db_used_mb) / 1024
                
                if at_capacity:
                    # Critical capacity warning
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - CRITICAL: Capacity Alert",
                        observation=f"Dataverse capacity at {db_usage}% ({db_used_mb:,} MB / {db_capacity_mb:,} MB) - IMMEDIATE action required to prevent service disruption",
                        recommendation=f"URGENT: Dataverse capacity critically high at {db_usage}%. Immediate actions required: 1) Purchase additional capacity NOW (budget {remaining_gb:.1f} GB shortfall), 2) Implement emergency data retention - delete conversation history older than 30 days, 3) Archive inactive agent data to Azure Storage, 4) Pause new agent deployments until capacity increased, 5) Review in Power Platform Admin Center daily. At this level, agent performance degrades and new conversations may fail. Prioritize capacity expansion over new feature development.",
                        link_text="Purchase Additional Capacity",
                        link_url="https://learn.microsoft.com/power-platform/admin/capacity-add-on",
                        priority="High",
                        status="Success"
                    )
                elif high_usage:
                    # High capacity warning
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - Capacity Warning",
                        observation=f"Dataverse capacity at {db_usage}% ({db_used_mb:,} MB / {db_capacity_mb:,} MB) - approaching limits, plan expansion",
                        recommendation=f"Dataverse usage at {db_usage}% - proactive capacity management needed: 1) Budget for {remaining_gb:.1f} GB additional capacity within 60 days, 2) Implement 90-day data retention policy for agent conversation history, 3) Archive completed workflows and old records, 4) Monitor usage weekly in admin center, 5) Plan capacity growth for agent adoption scaling. High usage restricts new agent deployments and limits data retention for contextual responses. Address before reaching 85%.",
                        link_text="Dataverse Capacity Management",
                        link_url="https://learn.microsoft.com/power-platform/admin/capacity-storage",
                        priority="Medium",
                        status="Success"
                    )
                else:
                    # Healthy capacity
                    deployment_rec = new_recommendation(
                        service="Power Platform",
                        feature=f"{feature_name} - Capacity Status",
                        observation=f"Dataverse capacity healthy at {db_usage}% ({remaining_gb:.1f} GB available) - sufficient headroom for agent growth",
                        recommendation=f"Current capacity ({db_usage}% used) supports agent expansion. Recommended actions: 1) Monitor capacity monthly in admin center, 2) Establish data governance (180-day retention as default), 3) Plan capacity growth: estimate 50-100 MB per active agent with conversation history, 4) Budget for capacity increases at 70% threshold. Good capacity posture enables aggressive agent deployment without near-term constraints.",
                        link_text="Dataverse Best Practices",
                        link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
                        priority="Low",
                        status="Success"
                    )
            else:
                # Fallback to user count estimation
                user_count = deployment.get('user_count', 0)
            if deployment.get('enterprise_scale'):
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Enterprise Capacity",
                    observation=f"Enterprise organization ({user_count} users) - premium Dataverse capacity critical for scale",
                    recommendation="Manage premium Dataverse capacity for enterprise agents: 1) Monitor storage consumption in Power Platform admin center monthly, 2) Plan for agent data growth: conversation history, user context, business data, 3) Implement data retention policies (90-180 day windows), 4) Optimize with table archival for historical data, 5) Budget for additional capacity as agent adoption grows. Large organizations need proactive capacity management to avoid service interruptions.",
                    link_text="Dataverse Capacity Management",
                    link_url="https://learn.microsoft.com/power-platform/admin/capacity-storage",
                    priority="Medium",
                    status="Success"
                )
            else:
                deployment_rec = new_recommendation(
                    service="Power Platform",
                    feature=f"{feature_name} - Capacity Planning",
                    observation=f"Organization size ({user_count} users) - premium capacity provides headroom for growth",
                    recommendation="Leverage premium Dataverse capacity: Monitor storage quarterly, establish data governance, plan for agent scale. Premium capacity supports ambitious agent deployments without near-term constraints.",
                    link_text="Dataverse Best Practices",
                    link_url="https://learn.microsoft.com/power-platform/admin/wp-cds-for-apps",
                    priority="Low",
                    status="Success"
                )
        else:
            deployment_rec = new_recommendation(
                service="Power Platform",
                feature=f"{feature_name} - Capacity",
                observation="Premium Dataverse capacity available",
                recommendation="Monitor premium database capacity in Power Platform admin center for agent data storage, conversation history, and business records.",
                link_text="Dataverse Admin",
                link_url="https://learn.microsoft.com/power-platform/admin/",
                priority="Low",
                status="Success"
            )
        return [license_rec, deployment_rec]
    return [license_rec]
