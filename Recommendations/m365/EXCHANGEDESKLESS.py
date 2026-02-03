"""
Exchange Online Kiosk - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Exchange Online Kiosk provides basic email for task workers
    with limited Copilot integration compared to full plans.
    """
    feature_name = "Exchange Online Kiosk"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing basic email access with limited AI capabilities",
            recommendation="",
            link_text="Task Worker Email",
            link_url="https://learn.microsoft.com/exchange/exchange-online/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing email infrastructure for task workers",
            recommendation=f"Enable {feature_name} to provide basic email access for frontline and task workers with limited Copilot needs. Kiosk provides 2GB mailboxes and web/mobile access sufficient for workers who primarily receive communications rather than create content. While not designed for full Copilot integration, it ensures all employees have email access that agents can use for notifications and updates. Consider upgrading task workers who would benefit from AI assistance to Plan 1 or Plan 2 for enhanced Copilot capabilities.",
            link_text="Task Worker Email",
            link_url="https://learn.microsoft.com/exchange/exchange-online/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    if status == "Success" and m365_insights and m365_insights.get('available'):
        email_active_users = m365_insights.get('email_active_users', 0)
        
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Task worker email: {email_active_users:,} email users. Exchange Online Kiosk provides basic email for frontline workers - 2GB mailboxes, web/mobile access. Limited Copilot integration but ensures all employees receive agent notifications and updates. Consider upgrading to full plans for AI assistance.",
            recommendation="",
            link_text="Kiosk Email",
            link_url="https://learn.microsoft.com/exchange/exchange-online/",
            status="Success"
        )
        recommendations.append(obs_rec)
    
    return recommendations
