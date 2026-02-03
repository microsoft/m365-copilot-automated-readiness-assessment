"""
Teams Premium - Virtual Appointments - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Teams Premium Virtual Appointments provides advanced scheduling
    and lobby features where agents can assist with appointment management.
    """
    recommendations = []
    
    feature_name = "Teams Premium - Virtual Appointments"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling agent-enhanced virtual appointment experiences",
            recommendation="",
            link_text="Advanced Virtual Appointments",
            link_url="https://learn.microsoft.com/microsoftteams/premium-virtual-appointments/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing advanced appointment capabilities for agents",
            recommendation=f"Enable {feature_name} to provide SMS notifications, queue management, and analytics for virtual appointments that agents can enhance. Build conversational agents that schedule appointments, send automated reminders, provide pre-appointment instructions, and collect post-visit feedback. Premium features include custom lobbies where agents can greet patients or customers, queue analytics to optimize staffing, and integration capabilities for agent-driven workflow automation in healthcare, financial services, and customer support scenarios.",
            link_text="Advanced Virtual Appointments",
            link_url="https://learn.microsoft.com/microsoftteams/premium-virtual-appointments/",
            priority="Low",
            status=status
        ))
    
    # M365 Insights - Agent-Enhanced Appointment Automation
    if m365_insights:
        teams_active_users = m365_insights.get('teams_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Virtual Appointments Premium enables Copilot Studio agents to manage entire appointment lifecycle - scheduling, reminders, pre-visit forms, lobby greetings, post-visit feedback. Advanced features: SMS notifications (reaching patients outside Teams), queue analytics for staffing optimization, custom branded lobbies where agents provide pre-appointment guidance. Critical for healthcare telehealth, financial advisor consultations, customer support appointments where agent automation improves efficiency and patient/customer experience.",
            recommendation="",
            link_text="Agent Appointment Automation",
            link_url="https://learn.microsoft.com/microsoftteams/premium-virtual-appointments/",
            status="Success"
        ))
        
        # Threshold-based recommendation
        if teams_total_meetings >= 500:
            recommendations.append(new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"With {teams_total_meetings} Teams meetings, premium virtual appointments can automate scheduling and patient/customer engagement workflows",
                recommendation=f"Deploy Virtual Appointments Premium for your organization conducting {teams_total_meetings} meetings. Build Copilot Studio agents that handle appointment scheduling, automated SMS reminders, pre-visit intake forms, lobby management, post-visit surveys. Essential for healthcare providers, financial advisors, customer support teams managing high-volume appointment workflows. Agents reduce administrative burden while improving appointment attendance and customer experience.",
                link_text="Premium Appointment Deployment",
                link_url="https://learn.microsoft.com/microsoftteams/premium-virtual-appointments/",
                status="Insight",
                priority="Medium"
            ))
    
    return recommendations
