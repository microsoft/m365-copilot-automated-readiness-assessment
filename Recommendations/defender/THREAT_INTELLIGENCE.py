"""
Microsoft Defender for Office 365 (Plan 2) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, defender_client=None, defender_insights=None):
    """
    Defender for Office 365 Plan 2 protects Copilot interactions from phishing,
    malware, and malicious prompts embedded in emails and documents.
    """
    feature_name = "Microsoft Defender for Office 365 (Plan 2)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        observation = f"{feature_name} is active, protecting Copilot workloads"
        recommendation = ""
        
        # Enrich with advanced threat intelligence from pre-computed insights
        if defender_insights and defender_insights.available:
            metrics = []
            
            # Combine email threats and incidents
            if defender_insights.has_email_threats():
                metrics.extend(defender_insights.phishing_malware_metrics)
            
            if defender_insights.incident_high_severity > 0:
                metrics.append(f"{defender_insights.incident_high_severity} high-severity incidents")
                recommendation = defender_insights.incident_recommendation
            
            if metrics:
                observation += ". " + ", ".join(metrics)
            else:
                # Clean status - no advanced threats
                observation += ". No advanced threats detected in last 30 days"
        
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
        observation=f"{feature_name} is {status} in {friendly_sku}, exposing Copilot to malicious content in emails and files",
        recommendation=f"Enable {feature_name} to protect M365 Copilot from processing malicious attachments, phishing attempts, and unsafe links. Defender analyzes threats before Copilot accesses email and SharePoint content, preventing AI from inadvertently spreading malware or responding to social engineering attacks embedded in documents.",
        link_text="Protect Copilot Data with Defender for Office 365",
        link_url="https://learn.microsoft.com/microsoft-365/security/office-365-security/mdo-about",
        priority="High",
        status=status
    )
