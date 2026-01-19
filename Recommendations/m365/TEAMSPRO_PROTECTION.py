"""
Teams Premium - Protection - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Teams Premium Protection provides advanced security features including
    watermarking and sensitivity labels for Copilot-generated meeting content.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Teams Premium - Protection"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, protecting sensitive Copilot-generated meeting content",
            recommendation="",
            link_text="Protect AI Meeting Content",
            link_url="https://learn.microsoft.com/microsoftteams/advanced-communications",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, exposing AI-generated meeting summaries to unauthorized sharing",
            recommendation=f"Enable {feature_name} to protect sensitive content in Copilot meeting summaries and transcripts. Apply watermarks to prevent screenshots of confidential AI-generated insights, enforce sensitivity labels on meeting recordings that Copilot references, and control who can access AI summaries of executive meetings. Premium Protection ensures that Copilot's convenient content generation doesn't create compliance risks by making sensitive discussions too easily shareable.",
            link_text="Protect AI Meeting Content",
            link_url="https://learn.microsoft.com/microsoftteams/advanced-communications",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        # ALWAYS create observation showing current protection context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"AI content security baseline: {teams_total_meetings:,} Teams meetings with {teams_active_users:,} active users generating Copilot summaries. Premium Protection prevents AI-generated content risks - watermarks stop screenshot leaks of confidential summaries, sensitivity labels restrict access to AI transcripts, and meeting intelligence access controls prevent unauthorized sharing. Copilot's convenience must not create compliance gaps.",
            recommendation="",
            link_text="AI Content Protection",
            link_url="https://learn.microsoft.com/microsoftteams/advanced-communications",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High meeting volume - protection critical
        if teams_total_meetings >= 200 and teams_active_users >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High meeting volume: {teams_total_meetings:,} meetings with {teams_active_users:,} Teams users. Premium Protection critical for securing AI-generated content.",
                recommendation="Deploy Premium Protection controls for sensitive meetings. Apply watermarks to Copilot summaries of executive meetings, enforce sensitivity labels on AI transcripts, and restrict access to meeting intelligence. Prevents compliance risks from easily shareable AI content.",
                link_text="Secure AI Content",
                link_url="https://learn.microsoft.com/microsoftteams/advanced-communications",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate meetings - establish protection
        elif teams_total_meetings >= 50 or teams_active_users >= 20:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing meeting culture: {teams_total_meetings:,} meetings with {teams_active_users:,} users. Premium Protection can secure AI meeting content.",
                recommendation="Implement Premium Protection for sensitive meeting categories (leadership, legal, customer). Test watermarking and sensitivity labels on AI summaries before expanding to all protected meetings.",
                link_text="Start Content Protection",
                link_url="https://learn.microsoft.com/microsoftteams/advanced-communications",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
        
    
    return recommendations
