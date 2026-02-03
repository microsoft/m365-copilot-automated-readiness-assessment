"""
Viva Insights - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name
from Core.spinner import get_timestamp

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Viva Insights provides AI-powered analytics on work patterns that help
    optimize how teams collaborate with Copilot and manage meeting load.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Viva Insights"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in Microsoft 365 Copilot, providing work pattern analytics to optimize Copilot usage",
            recommendation="",
            link_text="Optimize Collaboration with Viva Insights",
            link_url="https://learn.microsoft.com/viva/insights/introduction",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing analytics to optimize AI-assisted work patterns",
            recommendation=f"Enable {feature_name} to measure and improve how teams use Copilot and manage collaboration overload. Insights shows meeting hours saved through Copilot summaries, identifies teams spending excessive time in meetings who would benefit most from AI assistance, and tracks focus time that Copilot helps protect. Use these analytics to demonstrate Copilot ROI, identify adoption opportunities, and ensure AI tools genuinely improve work-life balance rather than just shifting workload.",
            link_text="Optimize Collaboration with Viva Insights",
            link_url="https://learn.microsoft.com/viva/insights/introduction",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_avg_meetings_per_user = m365_insights.get('teams_avg_meetings_per_user', 0)
        
        # High collaboration - analytics critical for optimization
        if teams_total_meetings > 200 and teams_avg_meetings_per_user > 3:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High collaboration activity: {teams_total_meetings:,} meetings across {teams_active_users:,} Teams users ({teams_avg_meetings_per_user:.1f} avg/user). {feature_name} can identify meeting overload patterns where Copilot summaries save maximum time.",
                recommendation="Use Viva Insights to identify teams with excessive meeting load (15+ hrs/week) who benefit most from Copilot meeting intelligence. Track reduction in meeting hours and increase in focus time as Copilot adoption grows. Insights data proves ROI by showing time reclaimed from meetings and email.",
                link_text="Optimize Collaboration with Viva Insights",
                link_url="https://learn.microsoft.com/viva/insights/introduction",
                priority="High",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate collaboration - track productivity trends
        elif teams_total_meetings > 50 and teams_active_users > 15:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate collaboration: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users ({teams_avg_meetings_per_user:.1f} avg/user). {feature_name} can track how Copilot improves meeting efficiency and work patterns.",
                recommendation="Deploy Viva Insights to establish baseline collaboration metrics before broader Copilot rollout. Measure meeting duration trends, after-hours work patterns, and focus time to quantify AI adoption impact.",
                link_text="Optimize Collaboration with Viva Insights",
                link_url="https://learn.microsoft.com/viva/insights/introduction",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low collaboration - foundational tracking
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Developing collaboration patterns with {teams_total_meetings:,} meetings. {feature_name} can establish work pattern baselines essential for measuring future Copilot impact.",
                recommendation="",
                link_text="Optimize Collaboration with Viva Insights",
                link_url="https://learn.microsoft.com/viva/insights/introduction",
                status="Success"
            )
            recommendations.append(obs_rec)

    
    return recommendations
