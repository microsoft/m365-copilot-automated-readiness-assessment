"""
Information Protection and Governance Analytics - Premium - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    Information Protection and Governance Analytics provides visibility into how
    sensitive data is being accessed, labeled, and shared through AI interactions.
    """
    feature_name = "Information Protection and Governance Analytics - Premium"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, tracking how Copilot accesses and processes protected content",
            recommendation="",
            link_text="Monitor AI Data Access Patterns",
            link_url="https://learn.microsoft.com/purview/data-classification-overview",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, lacking visibility into AI-driven data access patterns",
        recommendation=f"Enable {feature_name} to monitor and analyze how Copilot interacts with sensitive information across your organization. View dashboards showing which sensitivity labels Copilot encounters, track when users prompt AI to process confidential data, identify content with high sensitivity exposure through AI queries, and measure label adoption across AI-generated documents. Analytics reveal data governance gaps in Copilot workflows - such as unlabeled sensitive content being accessed, oversharing through AI summaries, or departments bypassing protection policies. Critical for demonstrating compliance in regulated industries deploying AI.",
        link_text="Monitor AI Data Access Patterns",
        link_url="https://learn.microsoft.com/purview/data-classification-overview",
        priority="Medium",
        status=status
    )
