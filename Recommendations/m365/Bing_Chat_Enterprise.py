"""
Bing Chat Enterprise - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Bing Chat Enterprise provides commercial data protection for web-based
    AI conversations, complementing M365 Copilot with internet knowledge.
    """
    feature_name = "Bing Chat Enterprise"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling secure web-grounded AI conversations",
            recommendation="",
            link_text="Secure Web AI with Bing Chat Enterprise",
            link_url="https://learn.microsoft.com/bing-chat-enterprise/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, forcing users to unprotected consumer AI for web research",
            recommendation=f"Enable {feature_name} to provide employees with commercial data protection when using AI for web research. While M365 Copilot focuses on organizational data, Bing Chat Enterprise accesses current web information with guarantees that prompts and responses aren't used for training or exposed to Microsoft. Use it for competitive research, industry trends, technical documentation, and market analysis where organizational data alone is insufficient. Prevents employees from using consumer ChatGPT and leaking company context.",
            link_text="Secure Web AI with Bing Chat Enterprise",
            link_url="https://learn.microsoft.com/bing-chat-enterprise/",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Web AI readiness: {total_active_users:,} users. Bing Chat Enterprise provides secure web-grounded AI - competitive research, industry trends, technical docs, market analysis. Complements M365 Copilot (internal data) with current web knowledge. Commercial data protection prevents leakage to consumer ChatGPT. Essential companion to organizational Copilot.",
            recommendation="",
            link_text="Bing Chat Enterprise",
            link_url="https://learn.microsoft.com/bing-chat-enterprise/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        if total_active_users >= 20:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"User base: {total_active_users:,} users likely need secure web AI for research and competitive intelligence.",
                recommendation="Train users on Bing Chat Enterprise for web-grounded AI tasks: competitive research, industry analysis, technical documentation lookups. Emphasize data protection vs consumer ChatGPT - prevents corporate context leakage. Position as M365 Copilot companion: Copilot for internal data, Bing Chat for web knowledge.",
                link_text="Bing Chat Training",
                link_url="https://learn.microsoft.com/bing-chat-enterprise/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
