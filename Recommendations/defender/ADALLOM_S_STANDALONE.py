"""
Microsoft Defender for Cloud Apps - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, defender_client=None, defender_insights=None):
    """
    Defender for Cloud Apps monitors Copilot data flows across cloud services
    and enforces DLP policies on AI-generated content and agent actions.
    """
    feature_name = "Microsoft Defender for Cloud Apps"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        observation = f"{feature_name} is active in {friendly_sku}, protecting Copilot workloads"
        recommendation = ""
        
        # Enrich with OAuth risk data from pre-computed insights
        if defender_insights and defender_insights.available:
            if defender_insights.has_oauth_risks():
                observation += ". " + ", ".join(defender_insights.oauth_metrics)
                recommendation = defender_insights.oauth_recommendation
            else:
                # Clean status - no OAuth risks
                observation += ". No high-risk OAuth apps detected"
        
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=observation,
            recommendation=recommendation,
            link_text="Cloud Apps",
            link_url="https://learn.microsoft.com/defender-cloud-apps/what-is-defender-for-cloud-apps",
            status=status
        )
    
    return new_recommendation(
        service="Defender",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, preventing governance of Copilot's cloud app integrations",
        recommendation=f"Enable {feature_name} to monitor and control how M365 Copilot and custom agents interact with cloud applications. Track file sharing triggered by AI assistants, enforce session controls when Copilot accesses third-party SaaS apps through plugins, and detect anomalous data access patterns by Copilot that may indicate compromised accounts or malicious prompts.",
        link_text="Cloud App Security for AI Services",
        link_url="https://learn.microsoft.com/defender-cloud-apps/what-is-defender-for-cloud-apps",
        priority="High",
        status=status
    )
