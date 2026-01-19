"""
Viva Learning (Seeded) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Viva Learning delivers AI-curated training content to help users
    learn Copilot skills and agent interaction best practices.
    """
    feature_name = "Viva Learning (Seeded)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-powered learning for Copilot skill development",
            recommendation="",
            link_text="Train Users on Copilot with Viva Learning",
            link_url="https://learn.microsoft.com/viva/learning/overview-viva-learning",
            status=status
        ))
        
        if m365_insights and m365_insights.get('available'):
            total_active_users = m365_insights.get('total_active_users', 0)
            teams_active_users = m365_insights.get('teams_active_users', 0)
            
            # ALWAYS create observation showing current metrics (no threshold)
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Current user metrics: {total_active_users:,} total active users with {teams_active_users:,} Teams users. Viva Learning can deliver Copilot training directly in Teams to accelerate AI adoption across your organization.",
                recommendation="",
                link_text="Copilot Training with Viva Learning",
                link_url="https://learn.microsoft.com/viva/learning/use-tabs",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        return recommendations
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, limiting structured learning for AI adoption",
        recommendation=f"Enable {feature_name} to deliver Copilot training directly in Teams. Curate learning paths teaching prompt engineering, agent interaction techniques, and feature-specific tutorials for Copilot in Word, Excel, and other apps. Viva Learning surfaces relevant training when users struggle with Copilot, tracks skill development, and ensures consistent AI literacy across the organization. Critical for driving adoption beyond early enthusiasts to mainstream users who need structured guidance.",
        link_text="Train Users on Copilot with Viva Learning",
        link_url="https://learn.microsoft.com/viva/learning/overview-viva-learning",
        priority="Medium",
        status=status
    ))
    return recommendations
