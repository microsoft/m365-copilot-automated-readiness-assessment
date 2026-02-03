"""
Microsoft Planner - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Planner provides task management for Copilot automation.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional M365 usage metrics
    """
    feature_name = "Microsoft Planner"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to automate task creation and tracking",
            recommendation="",
            link_text="Copilot Task Automation with Planner",
            link_url="https://learn.microsoft.com/office365/planner/planner-for-admins",
            status=status
        ))
        
        # NEW: Teams meetings proxy for project work
        if m365_insights and m365_insights.get('teams_report_available'):
            total_meetings = m365_insights.get('teams_total_meetings', 0)
            
            # Always generate observation with actual data
            if total_meetings > 500:
                # High - helpful
                recommendations.append(new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Collaboration",
                    observation=f"High meeting activity: {total_meetings:,} Teams meetings. Copilot can extract action items for Planner",
                    recommendation="",
                    link_text="",
                    link_url="",
                    priority="",
                    status=""
                ))
            elif total_meetings > 100:
                # Moderate
                recommendations.append(new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Collaboration",
                    observation=f"Moderate collaboration: {total_meetings:,} Teams meetings. Consider Planner integration to capture meeting action items",
                    recommendation="Deploy Planner for task management from Teams meetings. Integrating Planner helps capture action items, assign tasks, and track follow-ups directly from Teams conversations.",
                    link_text="Planner in Teams",
                    link_url="https://support.microsoft.com/office/use-planner-in-teams",
                    priority="Low",
                    status="Success"
                ))
            else:
                # Low
                recommendations.append(new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Collaboration",
                    observation=f"Low collaboration: Only {total_meetings:,} Teams meetings. Limited collaboration context for Planner adoption - establish teamwork patterns where Copilot can suggest tasks from meeting discussions and automatically track project progress.",
                    recommendation="Build collaboration foundation before deploying Planner. Focus on increasing Teams adoption first. Planner's value grows with team collaboration.",
                    link_text="Teams Adoption",
                    link_url="https://adoption.microsoft.com/microsoft-teams/",
                    priority="Low",
                    status="Success"
                ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing automated task management from Copilot",
            recommendation=f"Enable {feature_name} for Copilot task automation",
            link_text="Planner",
            link_url="https://learn.microsoft.com/office365/planner/planner-for-admins",
            priority="Medium",
            status=status
        ))
    
    return recommendations
