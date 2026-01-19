"""
Skype for Business Online (Plan 2) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Skype for Business Online is deprecated; users should migrate to
    Teams for full Copilot meeting intelligence capabilities.
    """
    feature_name = "Skype for Business Online (Plan 2)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}. Note: Skype for Business is deprecated; migrate to Teams for Copilot features",
            recommendation="",
            link_text="Migrate from Skype to Teams",
            link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
            status=status
        ))
        
        # M365 Insights - Show Teams adoption readiness
        if m365_insights and m365_insights.get('available'):
            teams_active_users = m365_insights.get('teams_active_users', 0)
            teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
            
            # Always create observation with current metrics
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Organization has {teams_active_users} active Teams users with {teams_total_meetings} meetings. Skype for Business is deprecated - complete migration to Teams for Copilot meeting intelligence.",
                recommendation="",
                link_text="Migrate from Skype to Teams",
                link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        return recommendations
    
    recommendations = []
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}. Skype for Business is retired and incompatible with Copilot",
        recommendation=f"Skype for Business Online was retired July 2021. Organizations still using Skype cannot leverage Copilot's meeting intelligence including transcription, recap, and action items. Migrate to Microsoft Teams immediately to enable AI-powered collaboration features. Teams provides comprehensive Copilot integration for meetings, chat, and calls - capabilities completely unavailable in legacy Skype infrastructure. This migration is prerequisite for any M365 Copilot adoption initiative.",
        link_text="Migrate from Skype to Teams",
        link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
        priority="High",
        status=status
    ))
    
    # M365 Insights - Show Teams adoption readiness
    if status == "Success" and m365_insights and m365_insights.get('available'):
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        if teams_active_users > 100:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Organization has {teams_active_users} active Teams users. Skype for Business is deprecated - complete migration to Teams to enable Copilot meeting intelligence.",
                recommendation="",
                link_text="Migrate from Skype to Teams",
                link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
    
    return recommendations
