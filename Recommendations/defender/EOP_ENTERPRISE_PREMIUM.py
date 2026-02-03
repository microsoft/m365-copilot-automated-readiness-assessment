"""
Microsoft Defender for Office 365 (Plan 1) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, defender_client=None, defender_insights=None):
    """
    Defender for Office 365 Plan 1 provides basic protection against
    malicious content that could be processed by Copilot.
    """
    feature_name = "Microsoft Defender for Office 365 (Plan 1)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        observation = f"{feature_name} is active, protecting Copilot workloads"
        recommendation = ""
        
        # Enrich with email threat metrics from pre-computed insights
        if defender_insights and defender_insights.available:
            if defender_insights.has_email_threats():
                observation += ". " + ", ".join(defender_insights.phishing_malware_metrics)
                recommendation = "Review email threats targeting Copilot users"
            else:
                # Clean status - no email threats
                observation += ". No email threats detected in last 30 days"
        
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=observation,
            recommendation=recommendation,
            link_text="Defender for Office 365",
            link_url="https://learn.microsoft.com/defender-office-365/",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, risking Copilot processing of malicious email content",
        recommendation=f"Enable {feature_name} to provide Safe Links and Safe Attachments protection for content Copilot accesses. When Copilot summarizes emails or creates responses, P1 ensures malicious URLs are rewritten and attachments are scanned before AI processes them. Prevents scenarios where Copilot inadvertently references or includes malicious content in generated responses, protecting both the AI system and users who act on Copilot recommendations based on email content.",
        link_text="Email Protection for Copilot",
        link_url="https://learn.microsoft.com/defender-office-365/",
        priority="High",
        status=status
    )
