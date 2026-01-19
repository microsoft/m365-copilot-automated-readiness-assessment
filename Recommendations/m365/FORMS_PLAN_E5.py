"""
Microsoft Forms (Plan E5) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Forms Plan E5 provides advanced features including branching
    logic and integrations that enable sophisticated agent-driven workflows.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft Forms (Plan E5)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling advanced agent-driven form workflows",
            recommendation="",
            link_text="Advanced Forms for Agent Workflows",
            link_url="https://learn.microsoft.com/microsoft-forms/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting sophisticated agent data collection",
            recommendation=f"Enable {feature_name} to create intelligent forms with conditional logic that agents use for complex workflows. Deploy agents that adapt form questions based on previous answers, integrate form responses with Power Automate for automated processing, and use Forms data to train agents on common user scenarios. E5 features enable agents to conduct sophisticated information gathering that adjusts dynamically to user context.",
            link_text="Advanced Forms for Agent Workflows",
            link_url="https://learn.microsoft.com/microsoft-forms/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use active users as proxy for feedback collection potential
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # Large user base - enterprise-scale feedback potential
        if total_active_users >= 500:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large user base of {total_active_users} active M365 users. Forms E5 enables sophisticated agent-driven surveys and feedback collection at enterprise scale.",
                recommendation="",
                link_text="Advanced Forms for Agent Workflows",
                link_url="https://learn.microsoft.com/microsoft-forms/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Medium user base - targeted intelligent forms
        elif total_active_users >= 100:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Medium-sized user base of {total_active_users} active M365 users. Forms E5 can enable intelligent data collection for agent training and process automation.",
                recommendation="Deploy adaptive Forms with conditional logic for Copilot adoption surveys. Integrate responses with Power Automate to trigger personalized training based on user needs.",
                link_text="Advanced Forms for Agent Workflows",
                link_url="https://learn.microsoft.com/microsoft-forms/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Small user base - focused feedback approach
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Smaller user base of {total_active_users} active M365 users. Forms E5 can establish structured feedback culture essential for agent improvement and adoption insights.",
                recommendation="Create intelligent Forms for continuous Copilot feedback collection. Use branching logic to gather detailed insights from different user personas (beginners vs. power users).",
                link_text="Advanced Forms for Agent Workflows",
                link_url="https://learn.microsoft.com/microsoft-forms/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
