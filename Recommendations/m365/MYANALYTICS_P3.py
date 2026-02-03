"""
Insights by MyAnalytics - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Insights by MyAnalytics provides basic personal productivity
    metrics that can show Copilot's impact on work patterns.
    """
    recommendations = []
    
    feature_name = "Insights by MyAnalytics"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing basic productivity insights alongside Copilot usage",
            recommendation="",
            link_text="Personal Productivity Insights",
            link_url="https://learn.microsoft.com/viva/insights/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing personal productivity analytics",
            recommendation=f"Enable {feature_name} to provide users with basic insights about meeting time, email patterns, and focus hours. While limited compared to full MyAnalytics, Insights helps users understand their work patterns and potentially correlate productivity improvements with Copilot adoption. Users can see if AI assistance reduces after-hours work, improves focus time, or decreases time spent in meetings by making them more efficient. Provides individual-level awareness that complements organizational Copilot adoption metrics.",
            link_text="Personal Productivity Insights",
            link_url="https://learn.microsoft.com/viva/insights/",
            priority="Low",
            status=status
        ))
    
    # M365 Insights - Personal Copilot ROI Measurement
    if m365_insights:
        total_active_users = m365_insights.get('total_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"MyAnalytics Plan 3 provides enhanced personal productivity analytics that correlate with Copilot usage - detailed focus time analysis, collaboration network insights, meeting quality metrics. Shows individual-level ROI: Does Copilot reduce after-hours work? Increase focus time? Improve meeting efficiency? Advanced analytics complement organizational dashboards with granular individual behavior changes. Essential for proving AI value at personal productivity level.",
            recommendation="",
            link_text="Personal Copilot ROI Analytics",
            link_url="https://learn.microsoft.com/viva/insights/",
            status="Success"
        ))
    
    return recommendations
