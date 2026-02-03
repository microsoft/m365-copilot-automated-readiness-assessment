"""
MyAnalytics (Full) - M365 & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    MyAnalytics (Full) provides detailed work pattern analytics and insights.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "MyAnalytics (Full)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing work pattern insights that correlate with Copilot adoption impact",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to provide users with insights into their work patterns and collaboration habits.",
            link_text="MyAnalytics Overview",
            link_url="https://learn.microsoft.com/viva/insights/personal/overview/mya-landing-page",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        # ALWAYS create observation showing current metrics (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Work analytics baseline: {total_active_users:,} active users with {email_active_users:,} email users and {teams_total_meetings:,} meetings. MyAnalytics provides the collaboration health metrics (focus time, meeting load, network breadth) that measure Copilot's ROI impact. Before AI: measure baseline work patterns. After AI: quantify time saved, meeting efficiency gains, and collaboration changes - proving Copilot business value.",
            recommendation="",
            link_text="Copilot ROI Analytics",
            link_url="https://learn.microsoft.com/viva/insights/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High collaboration activity - analytics valuable for ROI measurement
        if total_active_users >= 50 and teams_total_meetings >= 200:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High collaboration activity: {total_active_users:,} users with {teams_total_meetings:,} meetings. MyAnalytics can quantify Copilot ROI through meeting reduction and focus time improvements.",
                recommendation="Baseline current work patterns before Copilot rollout. Track meeting hours, focus time blocks, and after-hours work. Post-Copilot, measure improvements in these metrics to demonstrate AI value.",
                link_text="Measure Copilot ROI",
                link_url="https://learn.microsoft.com/viva/insights/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate activity - establish baseline
        elif total_active_users >= 15 and teams_total_meetings >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate collaboration: {total_active_users:,} users with {teams_total_meetings:,} meetings. MyAnalytics can track how Copilot improves work patterns and productivity.",
                recommendation="Use MyAnalytics to establish productivity baselines. Focus on measuring Copilot impact on email drafting time, meeting efficiency, and work-life balance metrics.",
                link_text="Track Productivity Improvements",
                link_url="https://learn.microsoft.com/viva/insights/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
