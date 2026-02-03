"""
Microsoft Entra ID Multi-Factor Authentication - License Check Only
Provides license status check. MFA enrollment analysis is in AAD_PREMIUM.py to avoid duplication.
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Generate MFA license check recommendation for Copilot security.
    
    Note: MFA enrollment analysis is handled by AAD_PREMIUM.py to avoid duplication,
    since P1 license includes MFA capabilities and provides the enrollment metrics.
    
    Args:
        sku_name: SKU name where feature is found
        status: Provisioning status
        client: Graph client (unused, for compatibility)
        entra_insights: Pre-computed identity metrics (unused here, used in AAD_PREMIUM)
    """
    feature_name = "Microsoft Entra ID Multi-Factor Authentication"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # Single observation: License check only
    if status == "Success":
        return new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, protecting Copilot sessions with additional authentication factors",
            recommendation="",
            link_text="MFA for Copilot Security",
            link_url="https://learn.microsoft.com/entra/identity/authentication/concept-mfa-howitworks",
            status=status
        )
    
    return new_recommendation(
        service="Entra",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, leaving Copilot access vulnerable to credential theft",
        recommendation=f"Enable {feature_name} immediately to require multi-factor authentication for M365 Copilot users. This prevents unauthorized access to AI assistants that can retrieve, summarize, and generate content from your organization's most sensitive data. MFA is a critical security baseline for AI adoption.",
        link_text="MFA for Copilot Security",
        link_url="https://learn.microsoft.com/entra/identity/authentication/concept-mfa-howitworks",
        priority="High",
        status=status
    )
