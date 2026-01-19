"""
Microsoft Viva Goals - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Viva Goals provides OKR tracking that Copilot can update based on
    progress discussions and automatically measure adoption metrics.
    """
    feature_name = "Microsoft Viva Goals"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-driven OKR tracking and progress updates",
            recommendation="",
            link_text="AI-Powered Goals Management",
            link_url="https://learn.microsoft.com/viva/goals/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing structured goal tracking for AI adoption",
            recommendation=f"Enable {feature_name} to track Copilot adoption as an organizational objective with measurable key results. Set goals like 'Achieve 80% Copilot active usage' or 'Reduce email drafting time by 30%', then use Viva Goals to monitor progress automatically. Copilot can update goal status based on usage analytics, suggest corrective actions when targets lag, and generate progress reports for leadership. Goals provides accountability framework for AI transformation, ensuring adoption initiatives remain visible and prioritized across the organization.",
            link_text="AI-Powered Goals Management",
            link_url="https://learn.microsoft.com/viva/goals/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"OKR tracking readiness: {total_active_users:,} users. Viva Goals enables structured objectives and key results - track Copilot adoption as organizational goal with measurable KRs. AI updates goal progress automatically from usage analytics. Framework for AI transformation accountability and visibility.",
            recommendation="",
            link_text="Viva Goals OKRs",
            link_url="https://learn.microsoft.com/viva/goals/",
            status="Success"
        )
        recommendations.append(obs_rec)
    
    return recommendations
