"""
Exchange Online Archiving for Exchange Online - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Exchange Online Archiving provides extended mailbox storage that
    Copilot can search for comprehensive email history analysis.
    """
    feature_name = "Exchange Online Archiving"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to access complete email history",
            recommendation="",
            link_text="Long-Term Email Intelligence",
            link_url="https://learn.microsoft.com/exchange/exchange-online-archiving/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting Copilot's access to historical email context",
            recommendation=f"Enable {feature_name} to extend mailbox storage and ensure Copilot can access complete email history. When users ask about past projects, customer interactions, or decision history, archiving ensures all relevant emails remain searchable and available to Copilot. Prevents knowledge gaps where important context exists in archived messages that Copilot cannot retrieve, particularly valuable for long-term customer relationships and institutional knowledge preservation in AI-assisted research.",
            link_text="Long-Term Email Intelligence",
            link_url="https://learn.microsoft.com/exchange/exchange-online-archiving/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    if status == "Success" and m365_insights and m365_insights.get('available'):
        email_active_users = m365_insights.get('email_active_users', 0)
        
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Email archiving: {email_active_users:,} email users. Exchange Online Archiving extends mailbox storage ensuring Copilot accesses complete email history. Critical for AI-assisted research into past projects, customer interactions, decision context. Prevents knowledge gaps from inaccessible archived messages.",
            recommendation="",
            link_text="Email Archiving",
            link_url="https://learn.microsoft.com/exchange/exchange-online-archiving/",
            status="Success"
        )
        recommendations.append(obs_rec)
    
    return recommendations
