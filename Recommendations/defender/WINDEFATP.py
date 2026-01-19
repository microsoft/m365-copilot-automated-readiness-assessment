"""
Microsoft Defender for Endpoint - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, defender_client=None, defender_insights=None):
    """
    Defender for Endpoint protects devices where users interact with Copilot,
    preventing AI-powered attacks and malicious prompt injection at the endpoint.
    """
    feature_name = "Microsoft Defender for Endpoint"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        observation = f"{feature_name} is active, protecting Copilot workloads"
        recommendation = ""
        
        # Enrich with incident and device metrics from pre-computed insights
        if defender_insights and defender_insights.available:
            metrics = []
            
            # Add incident metrics
            if defender_insights.has_incidents():
                metrics.extend(defender_insights.incident_metrics)
                recommendation = defender_insights.incident_recommendation
            
            # Add device metrics (only if Defender API available - requires onboarded devices)
            if defender_insights.defender_api_available:
                dev = defender_insights.defender_client.device_summary
                if dev.get('high_risk', 0) > 0:
                    metrics.append(f"{dev['high_risk']} high-risk devices")
                    if not recommendation:
                        recommendation = f"Secure {dev['high_risk']} high-risk device(s)"
            
            if metrics:
                observation += ". " + ", ".join(metrics)
            else:
                # Clean status - no incidents detected
                observation += ". No security incidents detected"
        
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=observation,
            recommendation=recommendation,
            link_text="Defender for Endpoint",
            link_url="https://learn.microsoft.com/microsoft-365/security/defender-endpoint/",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, leaving AI-enabled devices vulnerable to attacks",
        recommendation=f"Enable {feature_name} to protect the devices where employees use Copilot and agents. Endpoint security is critical because compromised devices could be used to inject malicious prompts, steal AI-generated sensitive data, or manipulate agent responses. Defender for Endpoint detects when attackers attempt to exploit AI interfaces, monitors for data exfiltration through copy/paste of Copilot outputs, and ensures that devices accessing powerful AI assistants meet security baselines. Essential for protecting the expanding attack surface created by AI adoption.",
        link_text="Endpoint Security for AI Workstations",
        link_url="https://learn.microsoft.com/microsoft-365/security/defender-endpoint/",
        priority="High",
        status=status
    )
