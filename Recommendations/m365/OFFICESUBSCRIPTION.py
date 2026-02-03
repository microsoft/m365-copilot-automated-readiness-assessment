"""
Microsoft 365 Apps for Enterprise - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft 365 Apps for Enterprise (Office apps) are the primary surface area
    where users interact with Copilot for document creation and data analysis.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft 365 Apps for Enterprise"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # License status (EXISTING - unchanged)
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing Word, Excel, PowerPoint, and Outlook with Copilot integration",
            recommendation="",
            link_text="Copilot in Office Applications",
            link_url="https://learn.microsoft.com/deployoffice/about-microsoft-365-apps",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing Copilot integration in productivity applications",
            recommendation=f"Enable {feature_name} to access the latest versions of Word, Excel, PowerPoint, Outlook, and OneNote with built-in Copilot capabilities. These apps are where employees spend most of their time and where Copilot delivers the most immediate value - drafting documents, analyzing data, creating presentations, and managing email. The enterprise version ensures Copilot features are available and that updates deliver new AI capabilities as Microsoft releases them. Without current Office apps, users cannot leverage Copilot's in-app assistance.",
            link_text="Copilot in Office Applications",
            link_url="https://learn.microsoft.com/deployoffice/about-microsoft-365-apps",
            priority="High",
            status=status
        ))
    
    # NEW: Office Activations Insights
    if status == "Success" and m365_insights and m365_insights.get('activations_report_available'):
        total_users = m365_insights.get('activations_total_users', 0)
        desktop_rate = m365_insights.get('activations_desktop_rate', 0)
        windows_users = m365_insights.get('activations_windows_users', 0)
        mac_users = m365_insights.get('activations_mac_users', 0)
        mobile_users = m365_insights.get('activations_mobile_users', 0)
        

        if desktop_rate >= 70:
            # HIGH DESKTOP ADOPTION - Excellent for Copilot
            recommendations.append(new_recommendation(
                service="M365",
                feature=f"{feature_name} - Desktop Adoption",
                observation=f"Strong desktop Office adoption: {desktop_rate}% of {total_users} users have desktop activations (Windows: {windows_users}, Mac: {mac_users}). Optimal for Copilot in-app experiences",
                recommendation="",  # No recommendation - this is HELPFUL
                link_text="Office Activations Report",
                link_url="https://learn.microsoft.com/microsoft-365/admin/activity-reports/microsoft-office-activations",
                status="Success"
            ))
        elif desktop_rate >= 40:
            # MODERATE - Mix of desktop and mobile/web
            recommendations.append(new_recommendation(
                service="M365",
                feature=f"{feature_name} - Desktop Adoption",
                observation=f"Mixed Office deployment: {desktop_rate}% desktop adoption ({windows_users} Windows, {mac_users} Mac) with {mobile_users} mobile-only users. Copilot works best in desktop apps",
                recommendation="Encourage desktop Office adoption for full Copilot experience. While Copilot works on web/mobile, desktop apps (Word, Excel, PowerPoint, Outlook) provide richer AI integration. Promote desktop installations, especially for knowledge workers and content creators. Mobile-only users get limited Copilot features.",
                link_text="Deploy Office Desktop Apps",
                link_url="https://learn.microsoft.com/deployoffice/deployment-guide-microsoft-365-apps",
                priority="Low",
                status="Success"
            ))
        else:
            # LOW DESKTOP - Mostly mobile/web
            recommendations.append(new_recommendation(
                service="M365",
                feature=f"{feature_name} - Desktop Adoption",
                observation=f"Low desktop Office adoption: Only {desktop_rate}% have desktop apps ({windows_users} Windows, {mac_users} Mac), {mobile_users} mobile-only. Limited Copilot capabilities",
                recommendation="Deploy desktop Office apps to maximize Copilot value. Low desktop adoption means most users can't access full Copilot features in Word, Excel, PowerPoint, Outlook. Web and mobile have limited AI capabilities. Deploy desktop Office to knowledge workers, content creators, data analysts - roles that benefit most from Copilot. Target 70%+ desktop adoption for effective Copilot program.",
                link_text="Office Deployment Guide",
                link_url="https://learn.microsoft.com/deployoffice/deployment-guide-microsoft-365-apps",
                priority="Medium",
                status="Warning"
            ))
    
    return recommendations if isinstance(recommendations, list) else [recommendations]
