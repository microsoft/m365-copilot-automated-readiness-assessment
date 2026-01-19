"""
Microsoft StaffHub - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft StaffHub has been retired and replaced by Shifts in
    Microsoft Teams for frontline worker scheduling.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft StaffHub"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}. Note: StaffHub is retired; migrate to Teams Shifts for AI-powered frontline worker scheduling",
            recommendation="",
            link_text="Use Teams Shifts Instead",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/shifts-for-teams-landing-page/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}. StaffHub was retired in 2020",
            recommendation=f"Microsoft StaffHub was retired in June 2020 and replaced by Shifts in Microsoft Teams. Use Teams Shifts for frontline worker schedule management with potential for AI-powered optimization. Shifts integrates with Teams where Copilot can assist with shift coverage requests, schedule conflict resolution, and automated notifications. Migration to Shifts enables modern frontline workforce management with future AI capabilities for intelligent scheduling and staffing predictions based on historical patterns.",
            link_text="Use Teams Shifts Instead",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/shifts-for-teams-landing-page/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)        
        # ALWAYS create observation showing current frontline context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Frontline workforce readiness: {total_active_users:,} users with {teams_active_users:,} Teams users. StaffHub RETIRED (2020) - Teams Shifts is the modern replacement with AI capabilities. Shifts enables Copilot-assisted schedule optimization, intelligent shift swap recommendations based on skills and availability, automated coverage suggestions when gaps detected, and predictive staffing needs from historical patterns. Essential infrastructure for frontline AI adoption.",
            recommendation="",
            link_text="Teams Shifts Migration",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/shifts-for-teams-landing-page/",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # Active Teams adoption - immediate migration opportunity
        if teams_active_users >= 20:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"URGENT: {teams_active_users:,} users on Teams but StaffHub still licensed. StaffHub retired 4+ years ago - critical migration gap for AI-powered scheduling.",
                recommendation="Immediately migrate to Teams Shifts. With {teams_active_users:,} Teams users, infrastructure exists for modern frontline management. Shifts enables AI schedule optimization, Copilot shift coverage assistance, and integration with Teams chat for shift-related communication. Every day on retired StaffHub delays frontline workforce AI capabilities.",
                link_text="Immediate Shifts Migration",
                link_url="https://learn.microsoft.com/microsoft-365/frontline/shifts-for-teams-landing-page/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
    return recommendations
