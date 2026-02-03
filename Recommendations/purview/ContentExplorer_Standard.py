"""
Content Explorer - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    Content Explorer provides visibility into labeled content that
    helps govern what information Copilot can access and process.
    """
    feature_name = "Content Explorer (Standard)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling visibility into content classifications for Copilot governance",
            recommendation="",
            link_text="Audit Copilot Data Access",
            link_url="https://learn.microsoft.com/purview/data-classification-content-explorer/",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, lacking visibility into what sensitive content Copilot accesses",
        recommendation=f"Enable {feature_name} to view and audit all labeled content across the tenant, providing transparency into what sensitive information Copilot can access. Content Explorer shows where confidential data resides, who has access, and which sensitivity labels are applied. Use it to identify oversharing of sensitive content that Copilot might inadvertently reference, audit compliance with data handling policies, and ensure appropriate restrictions on AI processing of highly classified information. Essential for risk assessment before broad Copilot deployment.",
        link_text="Audit Copilot Data Access",
        link_url="https://learn.microsoft.com/purview/data-classification-content-explorer/",
        priority="Medium",
        status=status
    )
