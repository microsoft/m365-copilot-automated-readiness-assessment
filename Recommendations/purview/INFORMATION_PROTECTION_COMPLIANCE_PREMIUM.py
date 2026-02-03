"""
Information Protection for Office 365 - Premium - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    Information Protection Premium provides automatic classification
    and advanced protection for Copilot-processed sensitive content.
    """
    feature_name = "Information Protection for Office 365 - Premium"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling automatic classification and advanced protection",
            recommendation="",
            link_text="Advanced Information Protection",
            link_url="https://learn.microsoft.com/purview/information-protection/",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing automatic classification for AI workflows",
        recommendation=f"Enable {feature_name} to automatically classify and protect sensitive content that Copilot accesses or generates. Premium adds automatic labeling based on content inspection, trainable classifiers for detecting specific content types, and advanced encryption options. When Copilot generates summaries containing sensitive data, Premium automatically applies appropriate labels and protections without user intervention. Essential for preventing accidental disclosure of sensitive information in AI-generated content, particularly in regulated industries with strict data handling requirements.",
        link_text="Advanced Information Protection",
        link_url="https://learn.microsoft.com/purview/information-protection/",
        priority="High",
        status=status
    )
