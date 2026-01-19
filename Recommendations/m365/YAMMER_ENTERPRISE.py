"""
Yammer Enterprise - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Yammer Enterprise provides social networking where communities
    can share Copilot tips and crowdsource AI use cases.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Yammer Enterprise"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling community knowledge sharing for Copilot adoption",
            recommendation="",
            link_text="Build Communities in Yammer",
            link_url="https://learn.microsoft.com/yammer/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing social collaboration platform",
            recommendation=f"Enable {feature_name} to create communities where employees share Copilot best practices, exchange prompt templates, and discuss AI use cases. Yammer provides a platform for organic AI adoption through peer learning, complementing formal training with real-world examples from colleagues. Use it to identify Copilot champions, surface innovative applications, and build grassroots enthusiasm for agent adoption across the organization.",
            link_text="Build Communities in Yammer",
            link_url="https://learn.microsoft.com/yammer/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations (same as VIVAENGAGE_CORE)
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        
        if total_active_users >= 500:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large user base of {total_active_users} active M365 users provides strong foundation for Copilot communities in Yammer. Enterprise-scale knowledge sharing potential.",
                recommendation="",
                link_text="Build Communities in Yammer",
                link_url="https://learn.microsoft.com/yammer/",
                status="Success"
            )
            recommendations.append(obs_rec)
        elif total_active_users >= 100:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Medium-sized user base of {total_active_users} active M365 users. Yammer can accelerate Copilot adoption through champion networks and crowdsourced best practices.",
                recommendation="Establish Yammer community for Copilot Champions with bi-weekly sharing sessions, prompt libraries, and success story showcases to scale adoption knowledge.",
                link_text="Build Communities in Yammer",
                link_url="https://learn.microsoft.com/yammer/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Smaller user base of {total_active_users} active M365 users. Yammer communities can establish peer-learning culture essential for AI adoption.",
                recommendation="Create focused Yammer community with weekly Copilot tips from power users. In smaller organizations, social knowledge transfer accelerates AI proficiency.",
                link_text="Build Communities in Yammer",
                link_url="https://learn.microsoft.com/yammer/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
