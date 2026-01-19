"""
Exchange Online Kiosk - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Exchange Online Kiosk provides limited email access for
    frontline workers who may interact with agents for basic tasks.
    """
    recommendations = []
    
    feature_name = "Exchange Online Kiosk"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing basic email for frontline workers who can use agent-assisted workflows",
            recommendation="",
            link_text="Frontline Email Service",
            link_url="https://learn.microsoft.com/exchange/clients-and-mobile-in-exchange-online/outlook-on-the-web/outlook-on-the-web-for-kiosk/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting email access for frontline workers",
            recommendation=f"Enable {feature_name} to provide basic email capabilities for frontline workers who benefit from simple agent interactions. While Kiosk users don't receive full M365 Copilot, they can interact with organizational agents built in Copilot Studio for tasks like shift swaps, equipment requests, policy lookups, and incident reporting. Agents democratize AI assistance for workers without premium licenses, enabling them to get answers and complete workflows through simple conversational interfaces rather than complex applications. Essential for extending AI benefits across entire workforce, not just information workers.",
            link_text="Frontline Email Service",
            link_url="https://learn.microsoft.com/exchange/clients-and-mobile-in-exchange-online/outlook-on-the-web/outlook-on-the-web-for-kiosk/",
            priority="Low",
            status=status
        ))
    
    # M365 Insights - Government Frontline Agent Access
    if m365_insights:
        email_active_users = m365_insights.get('email_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Exchange Kiosk (Government) provides basic 2GB email for public sector frontline workers - limited Copilot integration but ensures all employees receive agent notifications and updates. Government cloud compliance (GCC/GCC High) for sensitive communications. While kiosk users lack full AI features, they can interact with government-compliant Copilot Studio agents for policy lookups, equipment requests, incident reporting. Extends AI democratization to frontline government workforce.",
            recommendation="",
            link_text="Government Frontline Email",
            link_url="https://learn.microsoft.com/exchange/clients-and-mobile-in-exchange-online/outlook-on-the-web/outlook-on-the-web-for-kiosk/",
            status="Success"
        ))
    
    return recommendations
