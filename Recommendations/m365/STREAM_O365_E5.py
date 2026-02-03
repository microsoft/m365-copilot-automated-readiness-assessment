"""
Microsoft Stream for Office 365 (E5) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Stream (Plan 2) provides intelligent video hosting with AI-powered
    transcription, search, and content discovery that enhances knowledge sharing.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft Stream for Office 365 (E5)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-powered video intelligence and searchable transcripts",
            recommendation="",
            link_text="Intelligent Video with Stream",
            link_url="https://learn.microsoft.com/stream/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting AI-driven video knowledge capture",
            recommendation=f"Enable {feature_name} to provide intelligent video hosting with automatic transcription, speaker identification, and searchable content. Stream makes recorded meetings, training videos, and presentations discoverable through Copilot search - users can ask 'Find the video where we discussed the new product launch' or 'What did the CEO say about AI strategy?'. Copilot can summarize long videos, jump to relevant timestamps, and surface video content alongside documents in Business Chat. Critical for organizations building video-based knowledge repositories where Copilot transforms passive recordings into active searchable knowledge.",
            link_text="Intelligent Video with Stream",
            link_url="https://learn.microsoft.com/stream/",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use Teams metrics as proxy for video collaboration potential
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_messages = m365_insights.get('teams_total_messages', 0)
        
        
        # High meeting volume - strong video knowledge capture potential
        if teams_total_meetings > 1000:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High meeting volume of {teams_total_meetings} Teams meetings generates substantial video content. Stream with AI transcription makes this knowledge searchable through Copilot.",
                recommendation="",
                link_text="Intelligent Video with Stream",
                link_url="https://learn.microsoft.com/stream/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate meeting volume - opportunity for video knowledge base
        elif teams_total_meetings > 300:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate meeting volume of {teams_total_meetings} Teams meetings. Stream can transform recordings into searchable knowledge accessible via Copilot queries.",
                recommendation="Enable automatic Teams meeting recording to Stream with AI transcription. Train users to ask Copilot 'Find the video where we discussed X' to surface relevant meeting segments.",
                link_text="Intelligent Video with Stream",
                link_url="https://learn.microsoft.com/stream/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low meeting volume - establish video knowledge culture
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited meeting volume of {teams_total_meetings} Teams meetings. Stream can establish video-based knowledge capture culture that Copilot makes searchable and actionable.",
                recommendation="Launch training video initiative using Stream with AI transcription. Create searchable video library for onboarding, product demos, and how-to content that Copilot can surface contextually.",
                link_text="Intelligent Video with Stream",
                link_url="https://learn.microsoft.com/stream/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
