"""
Microsoft To Do (Plan 3) - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft To Do provides personal task management that Copilot can
    populate from emails and meetings for individual productivity.
    """
    feature_name = "Microsoft To Do (Plan 3)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to manage personal tasks automatically",
            recommendation="",
            link_text="AI Task Management with To Do",
            link_url="https://learn.microsoft.com/microsoft-365/todotasks/",
            status=status
        ))
        
        # M365 Insights - Task management adoption via email/meetings
        if m365_insights and m365_insights.get('available'):
            email_active_users = m365_insights.get('email_active_users', 0)
            teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
            
            # Always create observation with current metrics
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Email and meeting activity ({email_active_users} email users, {teams_total_meetings} meetings) generates personal tasks. To Do integrates with Copilot to capture action items automatically.",
                recommendation="",
                link_text="Task Management",
                link_url="https://learn.microsoft.com/microsoft-365/todotasks/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        return recommendations
    
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, preventing automated personal task creation",
        recommendation=f"Enable {feature_name} to let Copilot automatically create personal tasks from emails that contain requests, meeting action items assigned to specific users, and commitments made in conversations. To Do integrates with Outlook so Copilot can intelligently flag emails requiring follow-up and suggest task priorities based on deadlines and importance. This personal productivity layer ensures individual action items from Copilot don't get lost in the flow of collaboration.",
        link_text="AI Task Management with To Do",
        link_url="https://learn.microsoft.com/microsoft-365/todotasks/",
        priority="Low",
        status=status
    ))
    
    return recommendations
