"""
Microsoft 365 Phone System - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft 365 Phone System provides calling capabilities that
    conversational agents can integrate with for voice interactions.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft 365 Phone System"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling voice integration with conversational agents",
            recommendation="",
            link_text="Voice-Enabled Agent Interactions",
            link_url="https://learn.microsoft.com/microsoftteams/what-is-phone-system-in-office-365/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting voice-based agent interactions",
            recommendation=f"Enable {feature_name} to integrate telephony with conversational agents for voice-based customer service. Deploy agents that handle inbound calls, route to appropriate teams based on conversation analysis, transcribe voicemails and create tasks, and provide call summaries to agents. Phone System extends AI assistance beyond text chat into voice channels, supporting customer service centers and field workers who need hands-free access to organizational knowledge through Copilot-powered voice interactions.",
            link_text="Voice-Enabled Agent Interactions",
            link_url="https://learn.microsoft.com/microsoftteams/what-is-phone-system-in-office-365/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        # ALWAYS create observation showing current phone system context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Voice communication baseline: {teams_active_users:,} Teams users with {teams_total_meetings:,} meetings. Phone System extends Copilot intelligence beyond meetings and chat into voice channels - enabling AI call routing, automated voicemail transcription with action item extraction, call summaries, and hands-free knowledge access for field workers. Voice becomes an AI-powered channel.",
            recommendation="",
            link_text="Voice AI Integration",
            link_url="https://learn.microsoft.com/microsoftteams/what-is-phone-system-in-office-365/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High Teams usage - phone system adds voice channel
        if teams_active_users >= 50 and teams_total_meetings >= 150:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High Teams adoption: {teams_active_users:,} users with {teams_total_meetings:,} meetings. Phone System can add voice AI capabilities for customer service.",
                recommendation="Deploy Phone System to enable voice-based agent interactions. Integrate AI agents for call routing, voicemail transcription, and call summaries. Extends Copilot capabilities from meetings to voice calls for customer-facing teams.",
                link_text="Deploy Voice AI",
                link_url="https://learn.microsoft.com/microsoftteams/what-is-phone-system-in-office-365/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate Teams usage - consider voice integration
        elif teams_active_users >= 20 or teams_total_meetings >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing Teams usage: {teams_active_users:,} users with {teams_total_meetings:,} meetings. Phone System can extend AI to voice channels.",
                recommendation="Pilot Phone System with customer service teams. Test voicemail transcription and call summaries before expanding to full voice agent integration.",
                link_text="Start Voice AI",
                link_url="https://learn.microsoft.com/microsoftteams/what-is-phone-system-in-office-365/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
