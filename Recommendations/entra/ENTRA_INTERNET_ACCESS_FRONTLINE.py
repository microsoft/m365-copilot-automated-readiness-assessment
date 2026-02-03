"""
Entra Internet Access for Frontline - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Entra Internet Access for Frontline provides secure web access
    for frontline workers using organizational agents and basic AI features.
    
    Args:
        sku_name: SKU name where the feature is found
        status: Provisioning status
        client: Optional Graph client
        entra_insights: Optional dict with pre-computed metrics
    """
    feature_name = "Entra Internet Access for Frontline"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, securing frontline worker access to organizational agents",
            recommendation="",
            link_text="Frontline Secure Access",
            link_url="https://learn.microsoft.com/entra/global-secure-access/",
            status=status
        )
    
    return new_recommendation(
        service="Entra",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing secure web access for frontline agent interactions",
        recommendation=f"Enable {feature_name} to provide secure internet connectivity for frontline workers accessing organizational agents and basic AI services. Frontline workers may not have full Copilot licenses but can interact with custom agents for shift management, equipment requests, policy questions, and task guidance. Internet Access ensures these agent interactions remain secure, comply with organizational policies, and protect against web-based threats. Enables democratized AI access for non-desk workers while maintaining security controls, ensuring agents benefit entire workforce not just information workers with premium licenses.",
        link_text="Frontline Secure Access",
        link_url="https://learn.microsoft.com/entra/global-secure-access/",
        priority="Low",
        status=status
    )
