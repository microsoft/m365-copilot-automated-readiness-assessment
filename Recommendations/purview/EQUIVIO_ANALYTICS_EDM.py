"""
Exact Data Match Classification - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    Exact Data Match provides precise sensitive data detection
    that prevents Copilot from exposing specific protected values.
    """
    feature_name = "Exact Data Match Classification"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling precise detection of specific sensitive values in Copilot content",
            recommendation="",
            link_text="Precise Sensitive Data Protection",
            link_url="https://learn.microsoft.com/purview/sit-learn-about-exact-data-match-based-sits/",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, lacking precise sensitive data detection capabilities",
        recommendation=f"Enable {feature_name} to create custom sensitive information types based on exact values from databases (employee IDs, patient records, account numbers). EDM prevents Copilot from including specific protected values in responses even when patterns match generic sensitive information types. Upload hash tables of protected values so DLP policies can detect exact matches without storing plaintext, preventing false positives while ensuring genuine sensitive data is never surfaced by AI. Critical for healthcare, financial services, and government deploying Copilot with strict data protection requirements.",
        link_text="Precise Sensitive Data Protection",
        link_url="https://learn.microsoft.com/purview/sit-learn-about-exact-data-match-based-sits/",
        priority="Medium",
        status=status
    )
