"""
Viva Insights - MyAnalytics (Full) - M365 & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Viva Insights - MyAnalytics (Full) provides comprehensive work pattern analytics.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Viva Insights - MyAnalytics (Full)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing personal productivity analytics alongside Copilot usage",
            recommendation="",
            link_text="Personal Productivity Insights",
            link_url="https://learn.microsoft.com/viva/insights/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to provide comprehensive personal productivity insights and analytics. Track how Copilot adoption improves focus time, meeting efficiency, and work-life balance through measurable metrics.",
            link_text="Viva Insights Overview",
            link_url="https://learn.microsoft.com/viva/insights/introduction",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        
        # Large user base - enterprise-scale analytics
        if total_active_users >= 500:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large user base of {total_active_users:,} active M365 users with {teams_total_meetings:,} meetings. {feature_name} can measure Copilot's impact on productivity patterns at enterprise scale.",
                recommendation="",
                link_text="Personal Productivity Insights",
                link_url="https://learn.microsoft.com/viva/insights/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Medium user base - targeted insights
        elif total_active_users >= 20:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Medium-sized organization with {total_active_users:,} active users. {feature_name} can track how Copilot improves focus time, reduces meeting load, and enhances work-life balance.",
                recommendation="Launch MyAnalytics alongside Copilot training to help users measure productivity gains. Personal insights on time saved drafting emails/documents motivate continued AI adoption.",
                link_text="Personal Productivity Insights",
                link_url="https://learn.microsoft.com/viva/insights/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Small user base - focused deployment
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Smaller organization with {total_active_users:,} active users. {feature_name} can establish data-driven productivity culture where Copilot usage is measurably linked to wellbeing improvements.",
                recommendation="Enable MyAnalytics for leaders and power users first. Use personal productivity insights to demonstrate Copilot ROI through metrics like reduced after-hours work and increased focus time.",
                link_text="Personal Productivity Insights",
                link_url="https://learn.microsoft.com/viva/insights/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    
    return recommendations
