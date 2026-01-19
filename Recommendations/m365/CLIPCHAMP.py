"""
Clipchamp - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Clipchamp provides video editing that can be enhanced with AI for
    automated video creation from scripts and presentations.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Clipchamp"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing video creation capabilities for AI-generated content",
            recommendation="",
            link_text="AI-Assisted Video Creation",
            link_url="https://learn.microsoft.com/clipchamp/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting video content creation options",
            recommendation=f"Enable {feature_name} to create videos from Copilot-generated scripts and presentations. Use AI to transform PowerPoint presentations into narrated videos, generate training content from documentation, and create social media clips from meeting highlights. Clipchamp extends Copilot's content generation beyond text and slides into video format, supporting modern learning and communication preferences across distributed teams.",
            link_text="AI-Assisted Video Creation",
            link_url="https://learn.microsoft.com/clipchamp/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use Teams meetings as proxy for video content creation potential
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # High meeting volume - strong video creation opportunity
        if teams_total_meetings > 1000:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High meeting volume of {teams_total_meetings} Teams meetings. Clipchamp can transform meeting content into shareable video highlights, training materials, and executive summaries.",
                recommendation="",
                link_text="AI-Assisted Video Creation",
                link_url="https://learn.microsoft.com/clipchamp/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Moderate meeting volume - video editing opportunity
        elif teams_total_meetings > 300:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate meeting volume of {teams_total_meetings} Teams meetings. Clipchamp can create video summaries, training clips, and presentation recordings with AI assistance.",
                recommendation="Train content creators on Clipchamp for meeting highlights and training videos. Focus on L&D teams, marketing, and communications to create professional video content from meeting recordings and presentations.",
                link_text="AI-Assisted Video Creation",
                link_url="https://learn.microsoft.com/clipchamp/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Low meeting volume - establish video content culture
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited meeting activity with {teams_total_meetings} Teams meetings. Clipchamp with Copilot can help establish video-based communication culture - AI-powered video editing makes creating polished recordings accessible to all users.",
                recommendation="Launch Clipchamp training for creating video announcements, how-to guides, and product demos. Video content drives engagement in hybrid work - start with executive updates and employee onboarding materials.",
                link_text="AI-Assisted Video Creation",
                link_url="https://learn.microsoft.com/clipchamp/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
