"""
Queues App - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Queues App provides customer service queue management for
    frontline workers with potential agent integration.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Queues App"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling queue management with future agent capabilities",
            recommendation="",
            link_text="Service Queue Management",
            link_url="https://learn.microsoft.com/microsoftteams/manage-queues-app/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, lacking queue management for service operations",
            recommendation=f"Enable {feature_name} to manage customer service queues in Microsoft Teams with potential for future agent integration. Queues App helps frontline workers handle customer interactions efficiently, managing wait times and routing. While direct Copilot integration is limited, the structured queue data can inform agent development for automated triage, estimated wait time communication, and intelligent routing based on query classification. Relevant for retail, healthcare, and service organizations deploying both frontline collaboration and customer-facing agents.",
            link_text="Service Queue Management",
            link_url="https://learn.microsoft.com/microsoftteams/manage-queues-app/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        # ALWAYS create observation showing current service context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Service automation baseline: {total_active_users:,} users with {teams_active_users:,} Teams users. Queues App creates the workforce structure for conversational AI deployment - route customers to human agents OR bots, escalate from automated agents to specialists when needed, track interaction history that Copilot references. The foundational framework for hybrid human-AI customer service.",
            recommendation="",
            link_text="Frontline Queue Management",
            link_url="https://learn.microsoft.com/microsoftteams/manage-queues-app/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Large frontline workforce - queue management critical
        if total_active_users >= 50 and teams_active_users >= 25:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Substantial workforce: {total_active_users:,} users with {teams_active_users:,} Teams users. Queues App can streamline customer service operations and enable future agent automation.",
                recommendation="Deploy Queues App for customer-facing teams to manage service requests efficiently. Structured queue data establishes foundation for future AI agent triage, automated routing, and intelligent wait time predictions based on queue patterns.",
                link_text="Deploy Service Queues",
                link_url="https://learn.microsoft.com/microsoftteams/manage-queues-app/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate service team - targeted queue deployment
        elif total_active_users >= 15 and teams_active_users >= 10:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing service team: {total_active_users:,} users with {teams_active_users:,} Teams users. Queues App can organize customer interactions and prepare for agent-assisted service.",
                recommendation="Pilot Queues App with customer service or support teams. Start with single queue to manage incoming requests, then expand as workflows mature. Queue data will inform future agent automation for common inquiries.",
                link_text="Start Queue Management",
                link_url="https://learn.microsoft.com/microsoftteams/manage-queues-app/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
