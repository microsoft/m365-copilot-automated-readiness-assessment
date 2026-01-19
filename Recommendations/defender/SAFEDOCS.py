"""
Safe Documents (Microsoft 365 E5) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", defender_client=None, defender_insights=None):
    """
    Safe Documents provides cloud-based file scanning that protects
    users from malicious documents Copilot might reference or process.
    """
    feature_name = "Safe Documents"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        observation = f"{feature_name} is active in {friendly_sku}, protecting Copilot workloads"
        
        # Enrich with malware threat data from pre-computed insights
        if defender_insights and defender_insights.available:
            if defender_insights.alert_malware > 0:
                observation += f". {defender_insights.alert_malware} malware alerts"
                return new_recommendation(
                    service="Defender",
                    feature=feature_name,
                    observation=observation,
                    recommendation="Review malware detections in documents accessed by Copilot",
                    link_text="Safe Documents",
                    link_url="https://learn.microsoft.com/defender-office-365/safe-documents-in-e5-plus-security-about/",
                    status=status
                )
            else:
                # Clean status - no threats detected
                observation += ". No malware detected in last 30 days"
        
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=observation,
            recommendation="",
            link_text="Safe Documents",
            link_url="https://learn.microsoft.com/defender-office-365/safe-documents-in-e5-plus-security-about/",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, risking malware exposure when Copilot processes untrusted files",
        recommendation=f"Enable {feature_name} to scan documents opened in protected view using Microsoft Defender detonation chambers before Copilot accesses them. When users ask Copilot to summarize external documents or process downloaded files, Safe Documents verifies they're malware-free first. Prevents scenarios where Copilot inadvertently processes weaponized documents that exploit vulnerabilities, protecting both users and AI infrastructure from advanced threats embedded in seemingly benign content.",
        link_text="Document Protection for AI Workflows",
        link_url="https://learn.microsoft.com/defender-office-365/safe-documents-in-e5-plus-security-about/",
        priority="Medium",
        status=status
    )
