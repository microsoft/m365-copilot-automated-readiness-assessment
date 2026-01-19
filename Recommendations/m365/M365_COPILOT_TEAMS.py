"""
Microsoft 365 Copilot in Teams - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Copilot in Teams provides AI-powered meeting summaries, chat recaps,
    and intelligent collaboration features for hybrid work scenarios.
    """
    feature_name = "Microsoft 365 Copilot in Teams"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing AI meeting summaries and intelligent chat assistance",
            recommendation="",
            link_text="Copilot in Teams for Meetings",
            link_url="https://learn.microsoft.com/microsoftteams/copilot-teams-transcription",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing AI-powered meeting and chat capabilities",
            recommendation=f"Enable {feature_name} to transform Teams meetings and chats with AI. Get real-time meeting summaries with action items, catch up on missed meetings by asking 'What did I miss?', generate meeting recaps automatically, and get intelligent responses to questions during conversations. Copilot in Teams is essential for hybrid workers who need to stay aligned across time zones and manage meeting overload. It ensures no critical information is lost and reduces the time spent in status meetings.",
            link_text="Copilot in Teams for Meetings",
            link_url="https://learn.microsoft.com/microsoftteams/copilot-teams-transcription",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_avg_meetings_per_user = m365_insights.get('teams_avg_meetings_per_user', 0)        
        # ALWAYS create observation showing Teams Copilot meeting capabilities (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Teams meeting baseline: {total_active_users:,} users, {teams_active_users:,} Teams users, {teams_total_meetings:,} meetings (avg {teams_avg_meetings_per_user:.1f}/user). Teams Copilot transforms meeting overload - real-time summaries, action item extraction, 'What did I miss?' catch-up, chat Q&A during meetings. The MORE meetings ({teams_total_meetings:,}), the MORE time saved. Essential for hybrid work.",
            recommendation="",
            link_text="Teams Copilot Guide",
            link_url="https://learn.microsoft.com/microsoftteams/copilot-teams-transcription",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # Heavy meeting load - Teams Copilot critical
        if teams_total_meetings >= 150:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High meeting volume: {teams_total_meetings:,} meetings ({teams_avg_meetings_per_user:.1f} per user) indicate meeting overload. Teams Copilot essential.",
                recommendation="Deploy Teams Copilot training focused on meeting efficiency: Enable automatic meeting summaries for your {teams_total_meetings:,} meetings, teach users to ask 'What were the action items?' and 'Summarize decisions made', use chat Copilot for real-time Q&A during meetings. Measure time saved from not attending every meeting - users can review AI summaries instead. With {teams_avg_meetings_per_user:.1f} avg meetings per user, Copilot is critical productivity tool.",
                link_text="Teams Meeting AI",
                link_url="https://learn.microsoft.com/microsoftteams/copilot-teams-transcription",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)        
        # Moderate meetings - pilot Teams AI
        elif teams_total_meetings >= 50 or teams_active_users >= 20:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing meeting culture: {teams_total_meetings:,} meetings across {teams_active_users:,} Teams users. Pilot Teams Copilot for meeting efficiency.",
                recommendation="Pilot Teams Copilot with meeting-heavy roles: executives (leadership meetings), project managers (daily standups), customer-facing teams (client calls). Test meeting summaries, action item extraction, and catch-up features across your {teams_total_meetings:,} meetings. Track meeting time reduction and satisfaction before broader rollout.",
                link_text="Pilot Teams Copilot",
                link_url="https://learn.microsoft.com/microsoftteams/copilot-teams-transcription",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    return recommendations
