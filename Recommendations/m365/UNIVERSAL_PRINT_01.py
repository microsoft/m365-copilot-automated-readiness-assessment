"""
Universal Print - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Universal Print provides cloud-based printing that agents
    can use to automate document output workflows.
    """
    feature_name = "Universal Print"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling agent-initiated printing workflows",
            recommendation="",
            link_text="Cloud Printing Infrastructure",
            link_url="https://learn.microsoft.com/universal-print/",
            status=status
        ))
        
        if m365_insights and m365_insights.get('available'):
            total_active_users = m365_insights.get('total_active_users', 0)
            
            # ALWAYS create observation showing current metrics (no threshold)
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Current user metrics: {total_active_users:,} active users. Universal Print enables agent-automated printing workflows and eliminates print server maintenance for your organization.",
                recommendation="",
                link_text="Cloud Printing Infrastructure",
                link_url="https://learn.microsoft.com/universal-print/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        return recommendations
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, limiting automated document output",
        recommendation=f"Enable {feature_name} to let agents initiate printing as part of automated workflows. Build solutions where agents generate reports and automatically queue them for printing, route documents to specific printers based on content or location, and manage print jobs through conversational interfaces. Universal Print eliminates on-premises print server dependencies, supporting hybrid work while enabling agent-driven document automation for scenarios requiring physical output.",
        link_text="Cloud Printing Infrastructure",
        link_url="https://learn.microsoft.com/universal-print/",
        priority="Low",
        status=status
    ))
    return recommendations
