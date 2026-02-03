"""
Exchange Foundation - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Exchange Foundation provides core Exchange services for
    other workloads that may integrate with Copilot.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Exchange Foundation"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing messaging infrastructure that enables agent-triggered notifications and workflow communications",
            recommendation="",
            link_text="Exchange Foundation Infrastructure",
            link_url="https://learn.microsoft.com/exchange/exchange-online/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, lacking foundational Exchange services",
            recommendation=f"Enable {feature_name} to provide core Exchange infrastructure services including mailbox support, calendar, and basic messaging. While Foundation itself doesn't provide direct Copilot integration, it enables other M365 services that depend on Exchange capabilities. Acts as the messaging layer for notifications, workflow triggers, and system-generated communications that agents may use. Foundation is typically included automatically with other Exchange plans rather than licensed separately.",
            link_text="Exchange Foundation Infrastructure",
            link_url="https://learn.microsoft.com/exchange/exchange-online/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)        
        # ALWAYS create observation showing current messaging infrastructure context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Messaging infrastructure baseline: {total_active_users:,} users with {email_active_users:,} email users. Exchange Foundation is the backend infrastructure layer - NOT user-facing Copilot features but the messaging plumbing that enables notifications, calendar integrations, and workflow triggers. Supports agent-driven communications where automated systems send emails, meeting invites, or alerts. Foundational dependency for M365 Copilot email and calendar features.",
            recommendation="",
            link_text="Exchange Infrastructure",
            link_url="https://learn.microsoft.com/exchange/exchange-online/",
            status="Success"
        )
        recommendations.append(obs_rec)
    return recommendations
