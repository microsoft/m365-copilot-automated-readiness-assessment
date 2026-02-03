"""
Exchange Online Kiosk - M365 & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Exchange Online Kiosk provides basic email capabilities for kiosk and frontline workers.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Exchange Online Kiosk"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing email infrastructure that enables agent-triggered notifications for frontline workers",
            recommendation="",
            link_text="Frontline Email Infrastructure",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting frontline worker email access",
            recommendation=f"Enable {feature_name} to provide basic email access for frontline workers. Kiosk mailboxes support essential communication - automated shift notifications, schedule updates, and agent-triggered alerts for task assignments. While limited compared to full Exchange Online, Kiosk enables critical messaging infrastructure for field workers who need notifications but don't require full mailbox features.",
            link_text="Frontline Email Access",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)        
        # ALWAYS create observation showing current frontline communication context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Frontline communication baseline: {total_active_users:,} users with {email_active_users:,} email users and {teams_active_users:,} Teams users. Exchange Online Kiosk provides lightweight email for automated notifications - shift reminders, task assignments, schedule changes sent by agents or workflows. Not full Copilot integration, but essential notification infrastructure for frontline AI adoption where mobile workers need alert delivery without heavy mailbox features.",
            recommendation="",
            link_text="Frontline Notifications",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # Active frontline user base - consider full Exchange if needed
        if email_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large frontline email usage: {email_active_users:,} Kiosk mailbox users. If workers need more than basic notifications, consider upgrading to full Exchange Online for Copilot email assistance.",
                recommendation="Evaluate if frontline workers would benefit from full Exchange Online licenses with Copilot integration. If email is becoming a primary work tool (not just notifications), upgrade enables Copilot email drafting, inbox management, and intelligent categorization. If workers only need alerts and basic messages, Kiosk remains cost-effective.",
                link_text="Assess Email Needs",
                link_url="https://learn.microsoft.com/microsoft-365/frontline/flw-choose-scenarios",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    return recommendations
