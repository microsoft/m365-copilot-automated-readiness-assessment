"""
Microsoft Defender XDR - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", defender_client=None, defender_insights=None):
    """
    Defender XDR provides unified security for Copilot across endpoints, identities,
    email, and applications with advanced threat hunting and automated remediation.
    """
    feature_name = "Microsoft Defender XDR"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        observation = f"{feature_name} is active, protecting Copilot workloads"
        recommendation = ""
        
        # Enrich with XDR security metrics from pre-computed insights
        if defender_insights and defender_insights.available:
            metrics = []
            
            # Add incident data
            if defender_insights.has_incidents():
                metrics.extend(defender_insights.incident_metrics)
                recommendation = defender_insights.incident_recommendation
            
            # Add compromised users (Identity Protection)
            if defender_insights.risky_users_compromised > 0:
                metrics.append(f"{defender_insights.risky_users_compromised} compromised users")
                if not recommendation:
                    recommendation = defender_insights.identity_recommendation
            
            if metrics:
                observation += ". " + ", ".join(metrics)
            else:
                # Clean status - no incidents or identity risks
                observation += ". No security incidents detected"
        
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=observation,
            recommendation=recommendation,
            link_text="Defender XDR",
            link_url="https://learn.microsoft.com/microsoft-365/security/defender/",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, limiting visibility into Copilot security threats",
        recommendation=f"Enable {feature_name} to gain unified visibility and automated response across all M365 Copilot touchpoints - endpoints where users interact with AI, identities accessing Copilot, emails and files Copilot processes, and cloud apps integrated with agents. XDR correlates signals to detect prompt injection attacks and data exfiltration attempts through AI.",
        link_text="Unified Security for AI Workloads",
        link_url="https://learn.microsoft.com/microsoft-365/security/defender/microsoft-365-defender",
        priority="High",
        status=status
    )
