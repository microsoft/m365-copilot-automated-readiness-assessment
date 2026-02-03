"""
Skype for Business Online (Plan 1) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Skype for Business Online Plan 1 is a legacy communication
    platform being replaced by Microsoft Teams for agent interactions.
    """
    recommendations = []
    
    feature_name = "Skype for Business Online (Plan 1)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku} (legacy service - migrate to Teams for Copilot integration)",
            recommendation="",
            link_text="Skype to Teams Migration",
            link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku} (legacy service retired)",
            recommendation=f"Note: {feature_name} has been retired and replaced by Microsoft Teams. For Copilot and agent adoption, migrate communication workloads to Teams where M365 Copilot provides meeting summaries, chat assistance, and action item tracking. Teams enables agent integration through Copilot Studio, allowing custom agents to participate in conversations, answer questions, and automate workflows. Skype for Business lacks these AI capabilities, making migration essential for leveraging conversational AI in communication scenarios.",
            link_text="Skype to Teams Migration",
            link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
            priority="Low",
            status=status
        ))
    
    # M365 Insights - Government Cloud Legacy Migration
    if m365_insights:
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Skype for Business Online (Government) is retired legacy platform. Government agencies must migrate to Teams for Copilot integration in GCC/GCC High clouds. Teams provides government-compliant meeting summaries, chat assistance, action item tracking. Critical migration: Skype lacks all AI capabilities - no meeting transcription, no chat Copilot, no agent integration. For government Copilot adoption, complete Teams migration is prerequisite infrastructure.",
            recommendation="",
            link_text="Government Teams Migration",
            link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
            status="Success"
        ))
    
    return recommendations
