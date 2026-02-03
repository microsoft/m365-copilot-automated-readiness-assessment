"""
Microsoft Forms (Plan E1) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Forms enables creating surveys and quizzes that agents can
    use to collect structured feedback and automate data gathering workflows.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft Forms (Plan E1)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling agent-driven data collection and surveys",
            recommendation="",
            link_text="Agent-Powered Forms and Surveys",
            link_url="https://learn.microsoft.com/microsoft-forms/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting structured data collection for agents",
            recommendation=f"Enable {feature_name} to let agents create and distribute forms for data collection. Build conversational agents that generate Forms surveys based on user requests, automatically send feedback forms after service interactions, and analyze responses using Copilot to identify trends. Forms provides the structured data capture that complements Copilot's unstructured conversation analysis, essential for systematic feedback loops and decision support.",
            link_text="Agent-Powered Forms and Surveys",
            link_url="https://learn.microsoft.com/microsoft-forms/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        

        # ALWAYS create observation showing current forms context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Structured data foundation: {total_active_users:,} users with {email_active_users:,} email-active users. Forms provides the structured feedback capture that complements Copilot's unstructured conversation analysis. Agents generate surveys automatically, distribute post-interaction feedback forms, and Copilot analyzes aggregated responses to identify trends - creating systematic AI-driven feedback loops.",
            recommendation="",
            link_text="AI-Powered Data Collection",
            link_url="https://learn.microsoft.com/microsoft-forms/",
            status="Success"
        )
        recommendations.append(obs_rec)

        
        # Large user base - forms valuable for feedback
        if total_active_users >= 50 and email_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large organization: {total_active_users:,} users with {email_active_users:,} email users. Forms can enable AI-powered feedback collection at scale.",
                recommendation="Deploy Forms for automated feedback collection. Create agent-generated surveys after meetings, service interactions, or training events. Use Copilot to analyze form responses and identify trends across organization.",
                link_text="Deploy AI Feedback Collection",
                link_url="https://learn.microsoft.com/microsoft-forms/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate users - establish feedback workflows
        elif total_active_users >= 15 or email_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing organization: {total_active_users:,} users with {email_active_users:,} email users. Forms can enable structured AI-analyzed feedback.",
                recommendation="Pilot Forms for team feedback collection. Test automated post-meeting surveys and Copilot analysis of responses before scaling organization-wide.",
                link_text="Start Feedback Collection",
                link_url="https://learn.microsoft.com/microsoft-forms/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
