"""
Teams Premium - Webinars - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Teams Premium Webinars enables large-scale events with AI-powered
    Q&A agents, automated summaries, and intelligent attendee engagement.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Teams Premium - Webinars"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-enhanced webinar experiences at scale",
            recommendation="",
            link_text="AI-Powered Webinars in Teams",
            link_url="https://learn.microsoft.com/microsoftteams/plan-webinars",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing AI capabilities for large-scale events",
            recommendation=f"Enable {feature_name} to deploy agents that enhance webinars and large meetings. Use AI agents to answer common attendee questions during events, generate real-time summaries and key takeaways, analyze Q&A patterns to surface trending topics, and create personalized follow-up content for attendees. Premium Webinars with Copilot transforms passive viewing into interactive, AI-augmented learning experiences that extend engagement beyond the live event.",
            link_text="AI-Powered Webinars in Teams",
            link_url="https://learn.microsoft.com/microsoftteams/plan-webinars",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        
        # ALWAYS create observation showing current webinar context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Event collaboration baseline: {teams_total_meetings:,} Teams meetings with {teams_active_users:,} active users. Premium Webinars transform large-scale events with AI-powered Q&A agents, automated real-time summaries, and intelligent attendee engagement analytics - extending Copilot capabilities to broadcast scenarios where AI scales human expertise.",
            recommendation="",
            link_text="AI-Powered Webinars",
            link_url="https://learn.microsoft.com/microsoftteams/plan-webinars",
            status="Success"
        )
        recommendations.append(obs_rec)

        
        # High meeting volume - webinar platform valuable
        if teams_total_meetings >= 200 and teams_active_users >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High collaboration scale: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users. Premium Webinars can deliver AI-enhanced large-scale events.",
                recommendation="Deploy Premium Webinars for all-hands meetings, training sessions, and customer events. Enable AI agents for automated Q&A during events, real-time summary generation, and post-event content creation. Scales AI assistance beyond small meetings to organization-wide communications.",
                link_text="Deploy AI Webinars",
                link_url="https://learn.microsoft.com/microsoftteams/plan-webinars",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate meetings - consider webinars for scale
        elif teams_total_meetings >= 50 or teams_active_users >= 25:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing event needs: {teams_total_meetings:,} meetings with {teams_active_users:,} users. Premium Webinars can enhance large meetings with AI capabilities.",
                recommendation="Pilot Premium Webinars for quarterly all-hands or training events. Test AI-powered Q&A agents and automated summaries with large audiences before expanding to customer-facing webinars.",
                link_text="Start AI Webinars",
                link_url="https://learn.microsoft.com/microsoftteams/plan-webinars",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
