"""
Excel Advanced Analytics - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Excel Advanced Analytics provides data analysis capabilities that
    Copilot enhances with natural language query and automated insights.
    """
    feature_name = "Excel Advanced Analytics"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling advanced AI-powered data analysis in Excel",
            recommendation="",
            link_text="Copilot Advanced Analytics in Excel",
            link_url="https://learn.microsoft.com/microsoft-365/excel/",
            status=status
        ))
        
        if m365_insights and m365_insights.get('available'):
            total_active_users = m365_insights.get('total_active_users', 0)
            

            # ALWAYS create observation showing current metrics (no threshold)
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Current user metrics: {total_active_users:,} active users. Excel Advanced Analytics with Copilot democratizes data analysis through natural language queries and AI-powered insights across your organization.",
                recommendation="",
                link_text="Copilot Advanced Analytics in Excel",
                link_url="https://learn.microsoft.com/microsoft-365/excel/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        return recommendations
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, limiting advanced data analysis with AI",
        recommendation=f"Enable {feature_name} to unlock Copilot's most sophisticated Excel capabilities. Use AI to perform advanced statistical analysis, create predictive models through natural language ('Forecast next quarter sales based on trends'), generate complex formulas and DAX expressions, and identify data patterns and anomalies automatically. Advanced Analytics transforms Excel from manual spreadsheet work into an AI-powered analytics platform accessible to non-technical users through Copilot's conversational interface.",
        link_text="Copilot Advanced Analytics in Excel",
        link_url="https://learn.microsoft.com/microsoft-365/excel/",
        priority="Medium",
        status=status
    ))
    return recommendations
