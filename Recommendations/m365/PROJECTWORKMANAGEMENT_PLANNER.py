"""
Microsoft Planner - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Planner provides task management that Copilot can
    populate with action items from meetings and conversations.
    """
    recommendations = []
    
    feature_name = "Microsoft Planner"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to create and track team tasks",
            recommendation="",
            link_text="AI-Driven Task Management",
            link_url="https://learn.microsoft.com/office365/planner/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing collaborative task management for AI workflows",
            recommendation=f"Enable {feature_name} to let Copilot automatically create Planner tasks from meeting action items, email commitments, and chat conversations. When meetings conclude, Copilot can generate task cards assigned to appropriate team members with due dates based on discussed priorities. Planner provides the shared task visibility that ensures AI-identified action items get tracked and completed, bridging the gap between conversation and execution. Integrates with Teams and Outlook for seamless task management in the flow of work.",
            link_text="AI-Driven Task Management",
            link_url="https://learn.microsoft.com/office365/planner/",
            priority="Low",
            status=status
        ))
    
    # M365 Insights - Copilot Task Automation
    if m365_insights:
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Planner enables Copilot to automatically create tasks from meeting action items, email commitments, chat conversations. AI extracts deliverables from discussions and generates task cards with assignments, due dates, priorities. Bridges gap between conversation and execution - ensures AI-identified action items get tracked and completed. Critical infrastructure for Copilot task automation: 'create Planner task for this project', 'add action items from meeting to our plan'. Integrates Teams/Outlook for seamless AI-driven task management.",
            recommendation="",
            link_text="Copilot Task Automation",
            link_url="https://learn.microsoft.com/office365/planner/",
            status="Success"
        ))
        
        # Threshold-based recommendation
        if teams_active_users >= 40:
            recommendations.append(new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"With {teams_active_users} Teams users, Planner provides shared task visibility ensuring Copilot-generated action items get tracked and completed",
                recommendation=f"Deploy Planner for your {teams_active_users} Teams users to enable Copilot task automation. Train teams to let AI extract action items from meetings and conversations, automatically creating task cards with assignments and due dates. Planner ensures AI-identified deliverables don't get lost - provides shared visibility, progress tracking, completion accountability for Copilot-generated work items.",
                link_text="AI Task Management Deployment",
                link_url="https://learn.microsoft.com/office365/planner/",
                status="Insight",
                priority="Low"
            ))
    
    return recommendations
