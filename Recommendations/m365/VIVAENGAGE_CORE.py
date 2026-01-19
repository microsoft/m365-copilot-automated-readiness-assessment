"""
Viva Engage Core - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Viva Engage (formerly Yammer) provides enterprise social networking
    where communities share Copilot best practices and AI use cases.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Viva Engage Core"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling community-driven Copilot knowledge sharing",
            recommendation="",
            link_text="Build Copilot Communities in Viva Engage",
            link_url="https://learn.microsoft.com/viva/engage/overview",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing platform for Copilot community building",
            recommendation=f"Enable {feature_name} to create communities where employees share Copilot tips, prompt templates, and use cases. Build 'Copilot Champions' networks that demonstrate effective AI usage, crowdsource innovative applications of agents, and provide peer support for adoption challenges. Viva Engage amplifies organic adoption by letting successful users teach others, creating viral enthusiasm beyond formal training programs. Essential for scaling Copilot knowledge across large organizations.",
            link_text="Build Copilot Communities in Viva Engage",
            link_url="https://learn.microsoft.com/viva/engage/overview",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use total active users as proxy for community potential
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        
        # Large user base - strong community building potential
        if total_active_users >= 500:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large user base of {total_active_users} active M365 users provides strong foundation for Copilot communities in Viva Engage. Scale knowledge sharing through peer-to-peer networks.",
                recommendation="",
                link_text="Build Copilot Communities in Viva Engage",
                link_url="https://learn.microsoft.com/viva/engage/overview",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Medium user base - targeted community approach
        elif total_active_users >= 100:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Medium-sized user base of {total_active_users} active M365 users. Viva Engage can accelerate Copilot adoption through targeted champion communities and best practice sharing.",
                recommendation="Create Copilot Champions community in Viva Engage with monthly prompts challenges, success story showcases, and Q&A sessions to drive viral adoption across departments.",
                link_text="Build Copilot Communities in Viva Engage",
                link_url="https://learn.microsoft.com/viva/engage/overview",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Small user base - focused community strategy
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Smaller user base of {total_active_users} active M365 users. Viva Engage can establish knowledge-sharing culture critical for Copilot adoption at scale - agents need organizational knowledge graph built through community discussions.",
                recommendation="Launch focused Viva Engage community with weekly Copilot tips from power users. In smaller organizations, personal knowledge transfer through social platforms accelerates AI proficiency faster than formal training alone.",
                link_text="Build Copilot Communities in Viva Engage",
                link_url="https://learn.microsoft.com/viva/engage/overview",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
