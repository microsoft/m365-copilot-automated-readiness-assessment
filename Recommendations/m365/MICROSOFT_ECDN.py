"""
Microsoft eCDN - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft eCDN optimizes video delivery for Teams events
    where Copilot provides live transcription and summaries.
    """
    feature_name = "Microsoft eCDN"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # DEBUG: Log insights availability
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, optimizing video delivery for large Teams events with Copilot",
            recommendation="",
            link_text="Efficient Video Delivery",
            link_url="https://learn.microsoft.com/ecdn/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, potentially impacting large event video quality",
            recommendation=f"Enable {feature_name} to optimize bandwidth usage for large Teams live events and town halls where Copilot provides real-time transcription and Q&A. eCDN uses peer-to-peer delivery to reduce network congestion during company-wide broadcasts, ensuring smooth video delivery that Copilot needs for accurate transcription. Particularly valuable for organizations with limited WAN capacity hosting all-hands meetings where hundreds attend simultaneously. Improves both attendee experience and Copilot's ability to provide reliable meeting intelligence at scale.",
            link_text="Efficient Video Delivery",
            link_url="https://learn.microsoft.com/ecdn/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        
        # ALWAYS create observation showing eCDN infrastructure context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Video delivery infrastructure: {total_active_users:,} total users, {teams_active_users:,} Teams users. Microsoft eCDN optimizes bandwidth for large Teams live events using peer-to-peer delivery. Critical for town halls and all-hands where hundreds attend simultaneously - ensures smooth video for accurate Copilot transcription and Q&A. Infrastructure enabler for AI-assisted large events.",
            recommendation="",
            link_text="eCDN for Events",
            link_url="https://learn.microsoft.com/ecdn/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Large organization - eCDN valuable for company-wide events
        if total_active_users >= 100:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Organization scale: {total_active_users:,} users indicate potential for large all-hands events. eCDN optimizes bandwidth.",
                recommendation="Configure eCDN for company-wide Teams live events. With {total_active_users:,} users, town halls and all-hands meetings can overwhelm network bandwidth if all stream simultaneously. eCDN's peer-to-peer delivery reduces WAN congestion, ensuring smooth video for Copilot transcription. Test with next large event - monitor bandwidth savings and attendee experience quality.",
                link_text="eCDN Configuration",
                link_url="https://learn.microsoft.com/ecdn/",
                priority="Low",
                status="Insight"
            )
            recommendations.append(rec)
        
    
    return recommendations
