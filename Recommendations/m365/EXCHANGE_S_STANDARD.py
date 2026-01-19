"""
Exchange Online (Plan 2) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Exchange Online Plan 2 provides enterprise email and calendar
    that Copilot uses for communication intelligence and scheduling.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Exchange Online (Plan 2)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot email and calendar intelligence",
            recommendation="",
            link_text="Email AI with Copilot",
            link_url="https://learn.microsoft.com/exchange/exchange-online/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, critically limiting Copilot's email capabilities",
            recommendation=f"Enable {feature_name} to provide the email infrastructure for Copilot's communication intelligence. Copilot drafts email replies, summarizes long threads, extracts action items from messages, and finds information across mailbox history. Plan 2 includes 100GB mailboxes, advanced compliance features, and unlimited archiving that ensure Copilot has complete email context. Without Exchange Online, Copilot cannot access one of the most valuable organizational knowledge sources. Plan 2 is the foundation for AI-powered email productivity.",
            link_text="Email AI with Copilot",
            link_url="https://learn.microsoft.com/exchange/exchange-online/",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Email activity metrics
        email_active_users = m365_insights.get('email_active_users', 0)
        email_avg_sent_per_user = m365_insights.get('email_avg_sent_per_user', 0)
        
        # High email activity - Copilot email features highly valuable
        if email_active_users > 100 and email_avg_sent_per_user >= 10:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High email activity with {email_active_users} active users sending average {email_avg_sent_per_user:.1f} emails per user. Copilot email drafting and summarization will deliver significant time savings.",
                recommendation="",
                link_text="Email AI with Copilot",
                link_url="https://learn.microsoft.com/exchange/exchange-online/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate email activity - Copilot adds value
        elif email_active_users > 20 and email_avg_sent_per_user >= 5:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate email activity with {email_active_users} active users ({email_avg_sent_per_user:.1f} avg sent/user). Copilot can streamline email composition and thread management.",
                recommendation="Train users on Copilot email features: draft replies from bullet points, summarize long threads, and extract action items. Focus on power users who manage high email volume.",
                link_text="Email AI with Copilot",
                link_url="https://learn.microsoft.com/exchange/exchange-online/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low email activity - opportunity to establish email best practices
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited email activity with {email_active_users} active users ({email_avg_sent_per_user:.1f} avg sent/user). Copilot can help establish professional email communication patterns.",
                recommendation="Deploy Copilot email training to improve communication quality. Even low email volumes benefit from AI-assisted drafting for clarity, tone, and professionalism. Focus on customer-facing roles and leadership communications.",
                link_text="Email AI with Copilot",
                link_url="https://learn.microsoft.com/exchange/exchange-online/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    
    return recommendations
