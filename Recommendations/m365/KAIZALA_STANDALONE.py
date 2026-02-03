"""
Microsoft Kaizala - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Kaizala is deprecated and being retired in favor
    of Microsoft Teams for frontline worker communication.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft Kaizala"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku} - Frontline workers lack AI capabilities",
            recommendation=f"Migrate frontline workers from Kaizala to Microsoft Teams to enable AI-powered communication and agent assistance for deskless employees. Kaizala lacks Copilot integration, meaning frontline teams cannot benefit from intelligent message summarization, shift handoff automation, task prioritization, or AI-assisted knowledge discovery. Teams provides frontline-specific features with Copilot integration: walkie-talkie mode with AI transcription, shift scheduling with intelligent recommendations, approvals workflows with agent automation, and mobile-first collaboration where Copilot helps workers find procedures, safety information, and expert contacts. Migration brings frontline workers into the same AI-enhanced communication ecosystem as information workers, ensuring consistent experience and eliminating digital divide between desk and deskless employees.",
            link_text="Teams for Frontline with Copilot",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}. Kaizala is being retired",
            recommendation=f"Microsoft Kaizala is being retired in favor of Microsoft Teams for frontline workers. Migrate to Teams to enable AI-powered communication for frontline and information workers. Teams provides superior collaboration capabilities with Copilot integration for meeting summaries, chat assistance, and agent deployment. Kaizala lacks AI features and modern security controls available in Teams. Migration is necessary to provide frontline workers with modern, AI-enhanced collaboration tools aligned with the rest of the organization.",
            link_text="Migrate from Kaizala to Teams",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        
        # ALWAYS create observation showing migration urgency (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Frontline AI readiness: {total_active_users:,} total users with {teams_active_users:,} already on Teams but Kaizala still licensed (retired July 2023). Kaizala blocks frontline access to Copilot chat, AI-powered workflows, and agent-assisted task management. Every day on deprecated platform delays AI benefits for field workers who need Copilot most - hands-free knowledge access, voice-driven updates, automated task routing. Immediate Teams migration mandatory for frontline AI adoption.",
            recommendation="",
            link_text="Urgent Frontline Migration",
            link_url="https://learn.microsoft.com/microsoft-365/frontline/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Teams already adopted - immediate migration feasible
        if teams_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Teams infrastructure exists: {teams_active_users:,} users already on Teams. Kaizala users missing AI features available to Teams users - immediate migration recommended.",
                recommendation="Accelerate Kaizala to Teams migration immediately. With {teams_active_users:,} users already on Teams, infrastructure and adoption patterns are established. Migrate remaining Kaizala users to eliminate capability gap and enable AI-powered frontline collaboration.",
                link_text="Urgent: Migrate to Teams",
                link_url="https://learn.microsoft.com/microsoft-365/frontline/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Limited Teams adoption - parallel migration and adoption needed
        else:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Limited Teams presence: only {teams_active_users:,} Teams users. Kaizala migration requires concurrent Teams adoption strategy for frontline workers.",
                recommendation="Plan comprehensive migration combining Kaizala sunset with Teams frontline deployment. Focus on mobile-first training, shift handoff workflows, and walkie-talkie features to ease transition for deskless workers.",
                link_text="Plan Frontline Migration",
                link_url="https://learn.microsoft.com/microsoft-365/frontline/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
