"""
Virtual Appointments - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Virtual Appointments enables scheduling and conducting customer meetings
    where agents can provide AI-powered assistance and automated follow-up.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Virtual Appointments"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-assisted customer appointment experiences",
            recommendation="",
            link_text="Agent-Powered Customer Appointments",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/virtual-appointments",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing infrastructure for agent-assisted customer meetings",
            recommendation=f"Enable {feature_name} to integrate Copilot and agents into customer-facing appointments. Deploy agents that handle appointment scheduling through conversational interfaces, provide pre-meeting briefings to staff using Copilot summaries of customer history, and automate post-appointment follow-ups with AI-generated summaries. Virtual Appointments becomes an agent orchestration platform for customer service, healthcare consultations, financial advising, and other scheduled interactions where AI augments human expertise.",
            link_text="Agent-Powered Customer Appointments",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/virtual-appointments",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        # ALWAYS create observation showing current appointment context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Customer service baseline: {teams_total_meetings:,} Teams meetings with {teams_active_users:,} active users. Virtual Appointments become an agent orchestration platform - conversational AI handles booking workflows, Copilot briefs staff with customer history, and automated follow-ups generate AI summaries. Transforms scheduled customer interactions into AI-augmented experiences.",
            recommendation="",
            link_text="AI Customer Appointments",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/virtual-appointments",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High customer meeting activity - virtual appointments critical
        if teams_total_meetings >= 150 and teams_active_users >= 25:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High customer interaction: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users. Virtual Appointments can automate scheduling and enhance customer experiences.",
                recommendation="Deploy Virtual Appointments for customer-facing teams. Enable AI agents for automated booking, pre-meeting customer briefings using Copilot history summaries, and post-meeting follow-up generation. Scales personalized customer service with AI assistance.",
                link_text="Deploy Virtual Appointments",
                link_url="https://learn.microsoft.com/microsoft-365/frontline/virtual-appointments",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate meetings - pilot appointments
        elif teams_total_meetings >= 50 or teams_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing customer engagement: {teams_total_meetings:,} meetings with {teams_active_users:,} users. Virtual Appointments can improve scheduling efficiency.",
                recommendation="Pilot Virtual Appointments with one customer-facing team (support, sales, services). Test automated scheduling before expanding to AI-powered meeting briefings and summaries.",
                link_text="Start Virtual Appointments",
                link_url="https://learn.microsoft.com/microsoft-365/frontline/virtual-appointments",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
        
    
    return recommendations
