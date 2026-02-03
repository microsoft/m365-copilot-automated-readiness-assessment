"""
Premium Encryption - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Premium Encryption provides double key encryption for highly sensitive
    content that Copilot may need to access with additional security controls.
    """
    feature_name = "Premium Encryption"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing enhanced encryption for Copilot-accessible content",
            recommendation="",
            link_text="Double Key Encryption for AI Content",
            link_url="https://learn.microsoft.com/purview/double-key-encryption",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting encryption controls for AI-accessible data",
            recommendation=f"Enable {feature_name} to encrypt highly sensitive content with customer-controlled keys, ensuring even Microsoft cannot access it without explicit authorization. For organizations in regulated industries or handling state secrets, this provides confidence that Copilot's cloud processing of sensitive data maintains sovereignty requirements. Premium Encryption allows controlled AI adoption in scenarios where standard cloud encryption is insufficient for regulatory or contractual compliance.",
            link_text="Double Key Encryption for AI Content",
            link_url="https://learn.microsoft.com/purview/double-key-encryption",
            priority="Low",
            status=status
        )
    
    return [license_rec]
