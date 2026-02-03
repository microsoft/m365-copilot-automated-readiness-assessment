"""
Microsoft Defender for Cloud Apps Discovery - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, defender_client=None):
    """
    Cloud App Security Discovery identifies shadow IT and third-party
    apps that might integrate with Copilot or agents.
    """
    feature_name = "Microsoft Defender for Cloud Apps Discovery"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, monitoring for unauthorized app integrations with Copilot",
            recommendation="",
            link_text="Control Third-Party AI Apps",
            link_url="https://learn.microsoft.com/defender-cloud-apps/",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, risking unauthorized third-party AI tool usage",
        recommendation=f"Enable {feature_name} to discover unauthorized cloud apps and AI tools that users adopt outside of sanctioned Copilot deployments. Cloud App Discovery identifies shadow AI solutions that may lack proper security controls, violate data residency requirements, or create data exfiltration risks. Monitor for third-party AI assistants, chatbot integrations, and automation tools that users deploy independently, then guide them to approved Copilot solutions. Prevents fragmentation of AI adoption across uncontrolled platforms.",
        link_text="Control Third-Party AI Apps",
        link_url="https://learn.microsoft.com/defender-cloud-apps/",
        priority="Medium",
        status=status
    )
