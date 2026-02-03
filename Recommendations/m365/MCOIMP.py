"""
Skype for Business Online (Plan 1) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Skype for Business Online Plan 1 is deprecated; migrate to
    Teams for Copilot meeting and collaboration features.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Skype for Business Online (Plan 1)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku} - CRITICAL: Blocks Copilot adoption",
            recommendation=f"Immediately migrate remaining Skype for Business users to Microsoft Teams. Skype for Business (retired July 2021) is incompatible with M365 Copilot and prevents access to AI-powered meeting intelligence, intelligent recap, chat assistance, and agent deployment. Every user still on Skype represents a gap in your Copilot coverage where meeting content cannot be transcribed, summarized, or made searchable by AI. Teams migration is a prerequisite blocker for organization-wide Copilot rollout. Prioritize migration of leadership, sales teams, and customer-facing roles who benefit most from AI meeting assistance and follow-up automation.",
            link_text="Urgent: Migrate to Teams for Copilot",
            link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}. Skype for Business retired July 2021",
            recommendation=f"Skype for Business Online was retired in July 2021 and is incompatible with M365 Copilot. Organizations must migrate to Microsoft Teams to access AI-powered meeting intelligence, chat assistance, and collaborative features. Teams is the modern platform for Copilot integration, providing meeting transcription, recap, intelligent chat, and agent deployment capabilities completely unavailable in legacy Skype. Migration to Teams is mandatory prerequisite for any Copilot adoption initiative.",
            link_text="Migrate to Teams for Copilot",
            link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        
        # ALWAYS create observation showing migration urgency (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"CRITICAL Copilot blocker: {teams_active_users:,} users on Teams, but Skype for Business still active. Skype blocks ALL Copilot capabilities - no meeting intelligence, no AI summaries, no chat assistance, no agent deployment. Every Skype user represents a gap in AI coverage where conversations cannot be transcribed or enhanced. Immediate Teams migration mandatory for organization-wide Copilot rollout.",
            recommendation="",
            link_text="Urgent Teams Migration",
            link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High Teams adoption - migration infrastructure ready
        if teams_active_users >= 25:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Teams infrastructure exists: {teams_active_users:,} users already on Teams. Remaining Skype users block Copilot adoption - immediate migration required.",
                recommendation="Accelerate remaining Skype for Business to Teams migration immediately. With {teams_active_users:,} users already on Teams, migration infrastructure is proven. Complete migration to enable organization-wide Copilot access for meeting intelligence and AI assistance.",
                link_text="Complete Teams Migration",
                link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Limited Teams adoption - parallel migration needed
        else:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited Teams adoption: {teams_active_users:,} users on Teams. Skype to Teams migration required for Copilot access.",
                recommendation="Plan comprehensive Skype to Teams migration. Focus on user training, workflow migration, and ensuring Teams readiness before Copilot rollout. Skype compatibility blocks all AI features.",
                link_text="Plan Teams Migration",
                link_url="https://learn.microsoft.com/microsoftteams/skype-for-business-online-retirement/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
