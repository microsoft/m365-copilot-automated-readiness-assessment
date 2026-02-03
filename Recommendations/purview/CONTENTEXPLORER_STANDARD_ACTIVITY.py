"""
Activity Explorer - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    Activity Explorer provides auditing of label activities that
    tracks how users and Copilot interact with protected content.
    """
    feature_name = "Activity Explorer"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, tracking how Copilot and users handle labeled content",
            recommendation="",
            link_text="Monitor AI Content Activities",
            link_url="https://learn.microsoft.com/purview/data-classification-activity-explorer/",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing audit trail for content protection activities",
        recommendation=f"Enable {feature_name} to audit all actions involving labeled content, including when Copilot accesses, summarizes, or generates content with sensitivity labels. Activity Explorer tracks label application, removal, downgrade, and sharing events, providing forensic evidence for compliance investigations. Monitor whether users respect label guidance when sharing Copilot responses, detect unauthorized label removals on AI-generated content, and demonstrate regulatory compliance for AI systems handling protected data. Critical for audit requirements in regulated industries.",
        link_text="Monitor AI Content Activities",
        link_url="https://learn.microsoft.com/purview/data-classification-activity-explorer/",
        priority="Medium",
        status=status
    )
