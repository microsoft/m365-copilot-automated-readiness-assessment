"""
Content Explorer - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    Content Explorer enables visibility into what content Copilot
    can access and how that content is classified for protection.
    """
    feature_name = "Content Explorer (Premium)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing visibility into labeled content that Copilot accesses",
            recommendation="",
            link_text="Content Classification Visibility",
            link_url="https://learn.microsoft.com/purview/data-classification-content-explorer",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing visibility into content accessed by Copilot",
        recommendation=f"Enable {feature_name} to audit what sensitive information Copilot can reference when generating responses. See which documents with specific sensitivity labels are in Copilot's index, verify that highly confidential content is properly restricted, and validate that DLP policies prevent classified information from appearing in AI outputs. Content Explorer shows the classification landscape that determines what Copilot knows, helping governance teams ensure AI respects information protection boundaries and doesn't surface restricted data in responses.",
        link_text="Content Classification Visibility",
        link_url="https://learn.microsoft.com/purview/data-classification-content-explorer",
        priority="Medium",
        status=status
    )
