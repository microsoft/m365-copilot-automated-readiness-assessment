"""
Viva Insights - Teamwork Analytics - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Teamwork Analytics provides team-level collaboration insights that
    help measure the impact of Copilot on team productivity.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Viva Insights - Teamwork Analytics"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling team collaboration pattern analysis alongside AI adoption",
            recommendation="",
            link_text="Team Productivity Analytics",
            link_url="https://learn.microsoft.com/viva/insights/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing team-level collaboration insights",
            recommendation=f"Enable {feature_name} to understand how teams collaborate and how Copilot adoption affects collaboration patterns. Track metrics like meeting efficiency, network breadth, and cross-functional collaboration, then correlate them with Copilot usage to demonstrate ROI. Identify high-performing teams that leverage AI effectively and share their practices. Teamwork Analytics provides the data needed to optimize Copilot deployment strategies and measure organizational transformation.",
            link_text="Team Productivity Analytics",
            link_url="https://learn.microsoft.com/viva/insights/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use comprehensive collaboration metrics for teamwork analytics
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_avg_meetings_per_user = m365_insights.get('teams_avg_meetings_per_user', 0)
        teams_total_messages = m365_insights.get('teams_total_messages', 0)
        
        
        # High collaboration activity - rich analytics potential
        if teams_total_meetings > 1000 and teams_active_users > 100 and teams_total_messages > 10000:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High collaboration activity with {teams_total_meetings} meetings, {teams_active_users} Teams users, and {teams_total_messages} messages. Teamwork Analytics can measure Copilot's impact on team productivity patterns across enterprise.",
                recommendation="",
                link_text="Team Productivity Analytics",
                link_url="https://learn.microsoft.com/viva/insights/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate collaboration activity - analytics adds value
        elif teams_total_meetings > 300 and teams_active_users > 30:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate collaboration activity with {teams_total_meetings} meetings and {teams_active_users} Teams users ({teams_avg_meetings_per_user:.1f} avg/user). Teamwork Analytics can track how Copilot improves meeting efficiency and reduces communication overhead.",
                recommendation="Deploy Teamwork Analytics to establish baseline collaboration metrics before broader Copilot rollout. Track meeting duration trends, after-hours collaboration, and network diversity to measure AI adoption impact on team dynamics.",
                link_text="Team Productivity Analytics",
                link_url="https://learn.microsoft.com/viva/insights/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low collaboration activity - opportunity to establish data culture
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited collaboration activity with {teams_total_meetings} meetings and {teams_active_users} Teams users. Teamwork Analytics can establish data-driven culture where Copilot impact is measurably tracked and optimized.",
                recommendation="Enable Teamwork Analytics for leadership teams first. Use analytics to demonstrate Copilot's value through concrete metrics like time saved in meetings, reduced email volume, and improved focus time. Data-driven adoption narratives accelerate organizational AI acceptance.",
                link_text="Team Productivity Analytics",
                link_url="https://learn.microsoft.com/viva/insights/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    
    return recommendations
