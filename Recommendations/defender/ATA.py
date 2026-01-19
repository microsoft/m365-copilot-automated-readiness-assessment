"""
Microsoft Defender for Identity - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, defender_client=None, defender_insights=None):
    """
    Defender for Identity detects compromised accounts attempting to abuse
    Copilot to access and exfiltrate organizational data through AI.
    """
    feature_name = "Microsoft Defender for Identity"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        observation = f"{feature_name} is active, protecting Copilot workloads"
        recommendation = ""
        
        # Enrich with identity risk metrics from pre-computed insights
        if defender_insights and defender_insights.available:
            if defender_insights.has_identity_risks():
                observation += ". " + ", ".join(defender_insights.identity_metrics)
                recommendation = defender_insights.identity_recommendation
            else:
                # Clean status - no identity risks
                observation += ". No risky users or sign-ins detected"
        
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=observation,
            recommendation=recommendation,
            link_text="Defender for Identity",
            link_url="https://learn.microsoft.com/defender-for-identity/what-is",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing detection of compromised accounts using Copilot",
        recommendation=f"Enable {feature_name} to detect when stolen credentials are used to abuse Copilot for data theft. Attackers who compromise user accounts can use Copilot to quickly gather intelligence ('Summarize all M&A discussions from the last month'), identify valuable data, and exfiltrate information at scale. Defender for Identity detects anomalous Copilot usage patterns, unusual data access through AI, and reconnaissance activities where attackers use Copilot to map your organization. This is a critical security control because Copilot makes data discovery extremely efficient for both legitimate users and attackers.",
        link_text="Identity Protection for AI Access",
        link_url="https://learn.microsoft.com/defender-for-identity/what-is",
        priority="High",
        status=status
    )
