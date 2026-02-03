"""
Insights by MyAnalytics - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Insights by MyAnalytics (now Viva Insights Personal) provides
    personal productivity analytics to complement Copilot usage.
    """
    feature_name = "Insights by MyAnalytics"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing personal productivity analytics alongside Copilot usage",
            recommendation="",
            link_text="Personal Productivity Insights",
            link_url="https://learn.microsoft.com/viva/insights/",
            status=status
        ))
        
        if m365_insights and m365_insights.get('available'):
            total_active_users = m365_insights.get('total_active_users', 0)
            email_active_users = m365_insights.get('email_active_users', 0)
            
            # ALWAYS create observation showing current metrics (no threshold)
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Current user metrics: {total_active_users:,} total active users with {email_active_users:,} email users. Viva Insights Personal provides productivity analytics to track how Copilot impacts work patterns across your organization.",
                recommendation="",
                link_text="Personal Productivity Insights",
                link_url="https://learn.microsoft.com/viva/insights/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        return recommendations
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing personal productivity metrics for Copilot correlation",
        recommendation=f"Enable {feature_name} (now Viva Insights Personal) to provide individuals with productivity analytics that correlate with Copilot adoption. Track focus time, collaboration patterns, and meeting habits to understand how Copilot changes work behaviors. Personal insights show users their own work patterns alongside Copilot suggestions, creating feedback loop that reinforces AI-assisted productivity. Essential for demonstrating individual-level value of Copilot through metrics showing reduced meeting time, increased focus, or improved work-life balance.",
        link_text="Personal Productivity Insights",
        link_url="https://learn.microsoft.com/viva/insights/",
        priority="Low",
        status=status
    ))
    return recommendations
