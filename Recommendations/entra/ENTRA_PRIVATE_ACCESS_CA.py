"""
Conditional Access for Entra Private Access - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Conditional Access for Entra Private Access enforces
    policies when agents access internal applications.
    
    Args:
        sku_name: SKU name where the feature is found
        status: Provisioning status
        client: Optional Graph client
        entra_insights: Optional dict with pre-computed metrics
    """
    feature_name = "Conditional Access for Entra Private Access"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enforcing access policies for agent connections to internal apps",
            recommendation="",
            link_text="Private Access Policies",
            link_url="https://learn.microsoft.com/entra/identity/conditional-access/",
            status=status
        )
    
    return new_recommendation(
        service="Entra",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing policy enforcement for agent access to internal systems",
        recommendation=f"Enable {feature_name} to apply conditional access policies when agents connect to internal applications via Private Access. Enforce requirements like device compliance, authentication strength, and session controls when agents query databases, trigger workflows in legacy systems, or access on-premises resources. Ensure agents only access internal systems from managed contexts, require MFA for sensitive operations, and block access from compromised devices. Essential for Zero Trust agent architecture where AI assistants need internal data access but must comply with same security policies as human users.",
        link_text="Private Access Policies",
        link_url="https://learn.microsoft.com/entra/identity/conditional-access/",
        priority="Medium",
        status=status
    )
