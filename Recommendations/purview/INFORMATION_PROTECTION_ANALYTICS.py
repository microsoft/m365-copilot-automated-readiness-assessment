"""
Information Protection and Governance Analytics - Premium - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    IP&G Analytics Premium provides insights into data protection
    coverage and effectiveness for Copilot-accessed content.
    """
    feature_name = "Information Protection and Governance Analytics - Premium"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing analytics on data protection effectiveness for AI content",
            recommendation="",
            link_text="Data Protection Analytics",
            link_url="https://learn.microsoft.com/purview/data-classification-overview/",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, lacking visibility into protection coverage",
        recommendation=f"Enable {feature_name} to gain insights into information protection adoption and effectiveness across content that Copilot accesses. Analytics show which sensitive data types are most common, labeling coverage rates, DLP policy effectiveness, and trends in classification accuracy. Use these insights to identify gaps where Copilot might access unprotected sensitive content, measure protection maturity, and prioritize areas for enhanced controls. Premium analytics provide the visibility needed to continuously improve AI governance and demonstrate compliance with data protection regulations.",
        link_text="Data Protection Analytics",
        link_url="https://learn.microsoft.com/purview/data-classification-overview/",
        priority="Low",
        status=status
    )
