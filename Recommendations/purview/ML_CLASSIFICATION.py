"""
Exact Data Match Classification - Purview & Compliance Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    Exact Data Match Classification provides advanced data classification using precise matching.
    """
    feature_name = "Exact Data Match Classification"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, protecting sensitive data that Copilot may access with precise classification",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}",
        recommendation=f"Enable {feature_name} to classify sensitive data using exact data matching for precise data protection.",
        link_text="Exact Data Match",
        link_url="https://learn.microsoft.com/purview/sit-learn-about-exact-data-match-based-sits",
        priority="High",
        status=status
    )
