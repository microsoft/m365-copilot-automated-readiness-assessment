"""
Office for the Web - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Office for the Web enables browser-based editing with Copilot features.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional M365 usage metrics
    """
    feature_name = "Office for the Web (SharePoint)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot assistance in browser-based Office apps",
            recommendation="",
            link_text="Copilot in Office for the Web",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        ))
        
        # NEW: SharePoint page views indicate web usage
        if m365_insights and m365_insights.get('sharepoint_report_available'):
            page_views = m365_insights.get('sharepoint_total_page_views', 0)
            
            # Always generate observation with actual data
            if page_views > 10000:
                # High - helpful for Copilot
                recommendations.append(new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Web Usage",
                    observation=f"High web collaboration: {page_views:,} SharePoint page views indicate active Office for web usage",
                    recommendation="",
                    link_text="",
                    link_url="",
                    priority="",
                    status=""
                ))
            elif page_views > 1000:
                # Moderate - suggest improvement
                recommendations.append(new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Web Usage",
                    observation=f"Moderate web usage: {page_views:,} SharePoint page views. Consider promoting Office for web for improved mobile and browser-based productivity",
                    recommendation="Encourage Office for web adoption for browser-based editing. Promote browser-based editing for quick document edits, mobile access, and real-time collaboration without desktop app requirements.",
                    link_text="Office for Web Adoption",
                    link_url="https://learn.microsoft.com/microsoft-365-apps/",
                    priority="Low",
                    status="Success"
                ))
            else:
                # Low - action needed
                recommendations.append(new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Web Usage",
                    observation=f"Low web usage: Only {page_views:,} SharePoint page views. Office for web adoption appears minimal - establish browser-based Office usage for seamless Copilot integration without desktop installations.",
                    recommendation="Drive Office for web adoption for browser-based productivity. Users may be missing opportunities for quick edits, mobile access, and real-time collaboration. Educate users on browser-based editing capabilities.",
                    link_text="Office for Web Getting Started",
                    link_url="https://support.microsoft.com/office",
                    priority="Medium",
                    status="Warning"
                ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting browser-based Copilot access",
            recommendation=f"Enable {feature_name} for browser-based Copilot access",
            link_text="Office for Web",
            link_url="https://learn.microsoft.com/microsoft-365-apps/",
            priority="Medium",
            status=status
        ))
    
    return recommendations if isinstance(recommendations, list) else [recommendations]
