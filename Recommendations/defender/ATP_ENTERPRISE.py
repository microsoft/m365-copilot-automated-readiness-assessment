"""
Microsoft Defender for Office 365 (Plan 1) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", defender_client=None, defender_insights=None):
    """
    Defender for Office 365 Plan 1 provides baseline protection against phishing
    and malicious links in content that Copilot processes.
    """
    feature_name = "Microsoft Defender for Office 365 (Plan 1)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        observation = f"{feature_name} is active in {friendly_sku}, protecting Copilot workloads"
        recommendation = ""
        
        # Enrich with email/phishing threat data from pre-computed insights
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
            link_url="https://learn.microsoft.com/microsoft-365/security/office-365-security/mdo-about",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, exposing Copilot to malicious email and unsafe links",
        recommendation=f"Enable {feature_name} to provide baseline security for content Copilot accesses. Safe Links checks URLs in real-time before Copilot processes them, preventing the AI from inadvertently spreading malicious links in generated responses. Safe Attachments scans files before Copilot reads them, ensuring AI doesn't process malware-infected documents. While Plan 2 offers advanced features, Plan 1 provides essential protection that prevents Copilot from becoming a vector for spreading threats extracted from emails and documents.",
        link_text="Baseline Protection for Copilot Content",
        link_url="https://learn.microsoft.com/microsoft-365/security/office-365-security/mdo-about",
        priority="High",
        status=status
    )
