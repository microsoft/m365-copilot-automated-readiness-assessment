"""
Data Investigations - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success"):
    """
    Data Investigations enables detailed analysis of content
    including Copilot-generated artifacts and agent interactions.
    """
    feature_name = "Data Investigations"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        return new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling investigation of Copilot usage and AI-generated content",
            recommendation="",
            link_text="Content Investigation Tools",
            link_url="https://learn.microsoft.com/purview/ediscovery-overview/",
            status=status
        )
    
    return new_recommendation(
        service="Purview",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing capability to investigate AI-related data incidents",
        recommendation=f"Enable {feature_name} to conduct deep investigations into potential data incidents involving Copilot or agents. Investigate scenarios like suspected data exposure through AI responses, unauthorized information access via Copilot queries, or agent misuse for data collection. Data Investigations provides search, review, and analysis tools to reconstruct what information users accessed through AI, what Copilot generated based on sensitive content, and how agents processed confidential data. Essential for incident response when AI systems may have been involved in security events, regulatory violations, or policy breaches requiring detailed forensic analysis.",
        link_text="Content Investigation Tools",
        link_url="https://learn.microsoft.com/purview/ediscovery-overview/",
        priority="Medium",
        status=status
    )
