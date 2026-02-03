"""
Audio Conferencing - M365 & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Audio Conferencing allows users to join Teams meetings via phone.
    """
    recommendations = []
    
    feature_name = "Audio Conferencing"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to process dial-in participant contributions in meetings",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to allow users to join Teams meetings via dial-in phone numbers.",
            link_text="Audio Conferencing in Teams",
            link_url="https://learn.microsoft.com/microsoftteams/audio-conferencing-in-office-365",
            priority="Medium",
            status=status
        ))
    
    # M365 Insights - Enterprise Voice Virtual User Infrastructure
    if m365_insights:
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Enterprise Voice Virtual User provides phone system infrastructure for AI voice agents and automated attendants. Virtual users handle inbound calls, provide voice-based self-service through conversational AI, route calls intelligently. Foundation for voice bots: 'call our support line and agent answers common questions', 'automated appointment scheduling via phone'. Extends Copilot Studio agents beyond chat to voice channel - accessibility for phone-first users, integration with existing phone systems.",
            recommendation="",
            link_text="Voice Agent Infrastructure",
            link_url="https://learn.microsoft.com/microsoftteams/phone-system-virtual-users",
            status="Success"
        ))
    
    return recommendations
