"""
Microsoft Defender for IoT - Defender & Security Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, defender_client=None):
    """
    Microsoft Defender for IoT provides security monitoring for IoT and OT devices.
    """
    feature_name = "Microsoft Defender for IoT"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, securing IoT devices in environments where Copilot may access operational data",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}",
        recommendation=f"Enable {feature_name} to secure your IoT and OT devices with threat detection and vulnerability management.",
        link_text="Defender for IoT",
        link_url="https://learn.microsoft.com/azure/defender-for-iot/",
        priority="High",
        status=status
    )
