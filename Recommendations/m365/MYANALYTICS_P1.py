"""
MyAnalytics (Full) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    MyAnalytics Full (now Viva Insights Personal) provides
    individual productivity insights that complement Copilot usage analytics.
    """
    feature_name = "MyAnalytics (Full)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing personal productivity insights alongside Copilot analytics",
            recommendation="",
            link_text="Personal Productivity Analytics",
            link_url="https://learn.microsoft.com/viva/insights/personal/introduction/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing personal productivity insights for Copilot adoption analysis",
            recommendation=f"Enable {feature_name} (now Viva Insights Personal) to provide individuals with productivity metrics that correlate with Copilot usage. Track focus time, collaboration patterns, and meeting habits to understand how Copilot adoption changes work behaviors. Users see personalized insights about their work patterns alongside Copilot suggestions, creating feedback loop that reinforces AI-assisted productivity habits. Analytics show whether Copilot is actually reducing meeting time, increasing focus periods, or improving work-life balance, providing individual-level ROI metrics that complement organizational adoption dashboards.",
            link_text="Personal Productivity Analytics",
            link_url="https://learn.microsoft.com/viva/insights/personal/introduction/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Personal insights: {total_active_users:,} users. MyAnalytics (now Viva Insights Personal) provides individual productivity metrics that correlate with Copilot usage - focus time, collaboration patterns, meeting habits. Shows whether Copilot reduces meetings, increases focus, improves work-life balance. Individual ROI metrics complement organizational dashboards.",
            recommendation="",
            link_text="Personal Analytics",
            link_url="https://learn.microsoft.com/viva/insights/personal/introduction/",
            status="Success"
        )
        recommendations.append(obs_rec)
    
    return recommendations
