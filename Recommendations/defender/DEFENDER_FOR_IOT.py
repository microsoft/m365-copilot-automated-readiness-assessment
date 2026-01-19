"""
Microsoft Defender for IoT - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, defender_client=None):
    """
    Defender for IoT provides OT/IoT security monitoring that
    can be integrated with Security Copilot for threat analysis.
    """
    feature_name = "Microsoft Defender for IoT"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, protecting IoT/OT environments with Security Copilot integration",
            recommendation="",
            link_text="IoT Security with AI Analysis",
            link_url="https://learn.microsoft.com/defender-for-iot/",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, lacking IoT/OT security monitoring",
        recommendation=f"Enable {feature_name} to secure IoT and operational technology environments with AI-powered threat detection. While not directly related to M365 Copilot, Defender for IoT integrates with Security Copilot to provide natural language investigation of IoT threats, automated incident response for industrial control systems, and unified security operations across IT and OT environments. Relevant for manufacturing, healthcare, and critical infrastructure organizations deploying both M365 Copilot for knowledge workers and securing connected devices with AI-assisted security operations.",
        link_text="IoT Security with AI Analysis",
        link_url="https://learn.microsoft.com/defender-for-iot/",
        priority="Low",
        status=status
    )
