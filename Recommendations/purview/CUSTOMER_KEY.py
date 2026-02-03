"""
Customer Key - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Customer Key allows you to control encryption keys for data that Copilot
    processes, meeting regulatory requirements for key sovereignty.
    """
    feature_name = "Customer Key"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing encryption key control for Copilot-processed data",
            recommendation="",
            link_text="Sovereign Encryption for AI Data",
            link_url="https://learn.microsoft.com/purview/customer-key-overview",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting encryption sovereignty for AI workloads",
            recommendation=f"Enable {feature_name} to maintain control of root encryption keys for data Copilot accesses and generates. For organizations in jurisdictions with data sovereignty requirements or handling classified information, Customer Key ensures that revoking keys makes content unreadable even to Microsoft. This enables Copilot adoption in highly regulated sectors (government, defense, finance) where cloud AI was previously prohibited due to encryption control requirements.",
            link_text="Sovereign Encryption for AI Data",
            link_url="https://learn.microsoft.com/purview/customer-key-overview",
            priority="Low",
            status=status
        )
    
    return [license_rec]
