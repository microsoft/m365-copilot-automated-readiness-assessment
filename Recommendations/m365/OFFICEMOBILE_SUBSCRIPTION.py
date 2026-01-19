"""
Office for the Web - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Office for the Web provides browser-based Office apps where
    Copilot can assist without requiring desktop installations.
    """
    recommendations = []
    
    feature_name = "Office for the Web"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot assistance in browser-based Office apps",
            recommendation="",
            link_text="Web-Based Copilot Access",
            link_url="https://learn.microsoft.com/microsoft-365/office-web-apps/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting flexible Copilot access options",
            recommendation=f"Enable {feature_name} to provide browser-based Word, Excel, PowerPoint, and OneNote with Copilot integration. Office for the Web extends Copilot access to scenarios where desktop apps aren't installed - shared devices, guest access, mobile browsers, and Chromebook users. Ensures all users can leverage AI assistance regardless of their device or platform, supporting BYOD and flexible work arrangements. While not as full-featured as desktop Copilot, web apps provide essential AI capabilities for document creation and collaboration.",
            link_text="Web-Based Copilot Access",
            link_url="https://learn.microsoft.com/microsoft-365/office-web-apps/",
            priority="Medium",
            status=status
        ))
    
    # M365 Insights - Mobile/BYOD Copilot Access
    if m365_insights:
        total_active_users = m365_insights.get('total_active_users', 0)
        office_active_users = m365_insights.get('office_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Office Mobile Subscription enables Copilot on smartphones and tablets - Word/Excel/PowerPoint AI assistance without desktop access. Critical for BYOD environments, field workers, executives on-the-go. Mobile Copilot provides document creation, email composition, chat assistance from any device. Extends AI benefits beyond office desks to airports, client sites, home offices. Democratizes Copilot access across all work locations and device types.",
            recommendation="",
            link_text="Mobile Copilot Access",
            link_url="https://learn.microsoft.com/microsoft-365/office-mobile/",
            status="Success"
        ))
        
        # Threshold-based recommendation
        if office_active_users >= 30:
            recommendations.append(new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"With {office_active_users} Office users, mobile Copilot access enables AI assistance for field workers and executives who work from phones/tablets",
                recommendation=f"Deploy Office Mobile Subscription for your {office_active_users} Office users who work from mobile devices. Enable Copilot on smartphones/tablets for document editing, email composition, Teams chat on-the-go. Essential for field workers, sales teams, executives who need AI assistance outside traditional office environments. Mobile Copilot ensures productivity wherever work happens.",
                link_text="Mobile Copilot Deployment",
                link_url="https://learn.microsoft.com/microsoft-365/office-mobile/",
                status="Insight",
                priority="Low"
            ))
        
    
    return recommendations
