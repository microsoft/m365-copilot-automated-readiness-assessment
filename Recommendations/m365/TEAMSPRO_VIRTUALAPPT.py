"""
Teams Premium - Virtual Appointments - M365 & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Teams Premium - Virtual Appointments enables AI-assisted customer appointment experiences.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Teams Premium - Virtual Appointments"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling agent-assisted appointment scheduling and customer service automation",
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
            recommendation=f"Enable {feature_name} to provide AI-enhanced virtual appointment experiences for customers.",
            link_text="Virtual Appointments in Teams",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/virtual-appointments",
            priority="Medium",
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
            observation=f"Customer engagement baseline: {teams_total_meetings:,} Teams meetings with {teams_active_users:,} active users. Premium Virtual Appointments enables AI-powered customer service automation - agents handle scheduling, Copilot provides pre-meeting customer history briefings, and automated post-appointment follow-ups with AI-generated summaries transform customer interactions.",
            recommendation="",
            link_text="AI-Powered Appointments",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/virtual-appointments",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High customer service activity - virtual appointments valuable
        if teams_total_meetings >= 150 and teams_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High customer interaction volume: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users. Premium Virtual Appointments can automate scheduling and enhance customer experiences.",
                recommendation="Deploy Premium Virtual Appointments for customer-facing teams (healthcare, financial services, retail). Enable AI agents for automated scheduling, pre-meeting customer history briefings, and post-appointment follow-up generation. Transforms customer service from scheduled calls to AI-enhanced experiences.",
                link_text="Deploy Customer Appointments",
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
                observation=f"Growing customer engagement: {teams_total_meetings:,} meetings with {teams_active_users:,} users. Premium Virtual Appointments can improve customer service efficiency.",
                recommendation="Pilot Premium Virtual Appointments with customer service or sales teams. Start with automated scheduling for one service type, then expand to AI-powered briefings and follow-ups as workflows mature.",
                link_text="Start Virtual Appointments",
                link_url="https://learn.microsoft.com/microsoft-365/frontline/virtual-appointments",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
