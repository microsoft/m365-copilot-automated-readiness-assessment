"""
Exchange Analytics - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Exchange Analytics provides email pattern insights that complement
    Copilot's understanding of communication effectiveness.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Exchange Analytics"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing communication pattern insights alongside Copilot usage",
            recommendation="",
            link_text="Email Intelligence Analytics",
            link_url="https://learn.microsoft.com/viva/insights/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing email pattern analysis capabilities",
            recommendation=f"Enable {feature_name} to analyze email communication patterns and measure how Copilot improves email efficiency. Track metrics like response times, email volume, and after-hours communication, then correlate with Copilot adoption to demonstrate productivity gains. Exchange Analytics helps identify users who spend excessive time on email composition - prime candidates for Copilot adoption. Provides data for ROI calculations showing time saved through AI-assisted email drafting and summarization.",
            link_text="Email Intelligence Analytics",
            link_url="https://learn.microsoft.com/viva/insights/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        email_active_users = m365_insights.get('email_active_users', 0)
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        # ALWAYS create observation showing current email analytics context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Communication analytics baseline: {email_active_users:,} active email users out of {total_active_users:,} total users. Exchange Analytics reveals communication patterns (email volume, response times, network density) that contextualize Copilot's impact - identify communication bottlenecks AI can eliminate, measure email reduction from Copilot summaries, detect collaboration silos agents can bridge. The metrics layer for AI-driven communication transformation.",
            recommendation="",
            link_text="Email Intelligence",
            link_url="https://learn.microsoft.com/viva/insights/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # High email volume - strong ROI measurement opportunity
        if email_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"High email activity: {email_active_users:,} active email users. Exchange Analytics can quantify Copilot ROI through email drafting time reduction and improved response efficiency.",
                recommendation="Baseline email metrics before Copilot rollout: average drafting time, daily email volume, response times, after-hours email. Post-Copilot, track 30-40% reduction in composition time and improved email quality scores.",
                link_text="Measure Email Efficiency Gains",
                link_url="https://learn.microsoft.com/viva/insights/",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate email usage - establish baseline
        elif email_active_users >= 15:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Moderate email activity: {email_active_users:,} users actively using email. Exchange Analytics can track Copilot impact on communication efficiency.",
                recommendation="Use Exchange Analytics to identify heavy email users (10+ emails/day) as Copilot early adopters. Track their email patterns before/after Copilot to demonstrate time savings from AI-assisted drafting.",
                link_text="Track Communication Patterns",
                link_url="https://learn.microsoft.com/viva/insights/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
