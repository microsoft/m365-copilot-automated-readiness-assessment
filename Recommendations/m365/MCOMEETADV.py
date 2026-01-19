"""
Microsoft 365 Audio Conferencing - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Audio Conferencing enables Teams meetings with dial-in phone access,
    ensuring Copilot captures contributions from all participants including phone users.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft 365 Audio Conferencing"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to capture phone participant contributions in meeting summaries",
            recommendation="",
            link_text="Inclusive Meeting Intelligence",
            link_url="https://learn.microsoft.com/microsoftteams/audio-conferencing-in-office-365",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, limiting phone participant access to AI-enhanced meetings",
        recommendation=f"Enable {feature_name} to provide dial-in phone numbers for Teams meetings, ensuring all participants can join and contribute to Copilot-summarized discussions. When users join via phone (traveling, poor internet, mobile-only), Copilot still captures their audio contributions for transcription, meeting summaries, and action items. Essential for global organizations where connectivity varies and for ensuring compliance requirements around meeting documentation capture all participants, regardless of how they join. Audio Conferencing democratizes access to AI-enhanced meetings beyond those with reliable internet.",
        link_text="Inclusive Meeting Intelligence",
        link_url="https://learn.microsoft.com/microsoftteams/audio-conferencing-in-office-365",
        priority="Medium",
        status=status
    )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        
        # ALWAYS create observation showing current meeting context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Meeting collaboration baseline: {teams_total_meetings:,} Teams meetings with {teams_active_users:,} active users. Audio Conferencing ensures Copilot meeting intelligence captures ALL participants - including phone dial-in users - enabling comprehensive AI summaries, action items, and transcripts regardless of connection method. Critical for inclusive AI-enhanced collaboration.",
            recommendation="",
            link_text="Inclusive Meeting Intelligence",
            link_url="https://learn.microsoft.com/microsoftteams/audio-conferencing-in-office-365",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High meeting volume - audio conferencing critical for inclusion
        if teams_total_meetings >= 200 and teams_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High collaboration activity: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users. Audio Conferencing ensures phone participants contribute to Copilot-summarized meetings.",
                recommendation="Promote Audio Conferencing dial-in numbers for all meetings to ensure phone participants (traveling users, poor connectivity) are captured in Copilot transcripts and summaries. Global organizations benefit from inclusive meeting intelligence regardless of participant connection method.",
                link_text="Inclusive Meeting Intelligence",
                link_url="https://learn.microsoft.com/microsoftteams/audio-conferencing-in-office-365",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate meetings - growing need for accessibility
        elif teams_total_meetings >= 50 or teams_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing meeting culture: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users. Audio Conferencing ensures all participants can contribute to AI-enhanced meetings.",
                recommendation="Enable Audio Conferencing for external meetings and mobile-heavy scenarios to ensure Copilot captures all participants. Essential for distributed teams where connectivity varies.",
                link_text="Accessible Meeting Intelligence",
                link_url="https://learn.microsoft.com/microsoftteams/audio-conferencing-in-office-365",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
