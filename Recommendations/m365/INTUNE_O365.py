"""
Microsoft Intune for Office 365 - Mobile Device/App Management for Office Apps
Provides basic MDM/MAM capabilities for phones and tablets accessing Office 365 apps.
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Intune for Office 365 provides limited mobile device and app management
    for phones/tablets accessing Office apps. Available in lower SKUs (Business Basic/Standard).
    
    Key capabilities:
    - Enroll mobile devices (iOS/Android) for Office app access
    - Protect corporate data in Office mobile apps (Outlook, Teams, OneDrive, Word, Excel, PowerPoint)
    - Enforce app protection policies (PIN, encryption, copy/paste restrictions)
    - Basic device compliance for mobile devices only
    
    NOT included (requires Intune Plan 1/2):
    - Windows PC management
    - Full Conditional Access integration
    - Advanced compliance policies
    - Remote wipe for all device types
    """
    feature_name = "Microsoft Intune for Office 365"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling basic mobile app protection for Office 365 on phones and tablets",
            recommendation="",
            link_text="Mobile App Management",
            link_url="https://learn.microsoft.com/mem/intune/fundamentals/mdm-authority-set",
            status=status
        ))
        
        # M365 Insights - Mobile readiness via total users
        if m365_insights and m365_insights.get('available'):
            total_active_users = m365_insights.get('total_active_users', 0)
            
            # Always create observation with current metrics
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Organization has {total_active_users} users. Mobile app management protects Copilot data on phones/tablets accessing Office apps.",
                recommendation="",
                link_text="Mobile App Protection",
                link_url="https://learn.microsoft.com/mem/intune/apps/app-protection-policy",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        return recommendations
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, lacking mobile app protection for Copilot on phones/tablets",
        recommendation=f"Enable {feature_name} to protect Copilot data on mobile devices (phones and tablets). Without mobile app management, users accessing Copilot on mobile devices can: 1) Copy/paste AI-generated summaries containing sensitive data to personal apps, 2) Take screenshots of Copilot responses without DLP enforcement, 3) Store Office files with Copilot content on unencrypted devices, 4) Access Copilot from jailbroken/rooted devices bypassing security. Configure Mobile Application Management (MAM) policies for Office apps to: require app PIN for Copilot access, prevent copy/paste and screenshots, encrypt app data at rest, block managed apps on non-compliant devices. Available in Business Basic/Standard tiers - provides essential mobile protection without full Intune licensing. Start with protecting Outlook, Teams, and OneDrive mobile apps where Copilot is integrated.",
        link_text="Mobile App Protection Policies",
        link_url="https://learn.microsoft.com/mem/intune/apps/app-protection-policy",
        priority="Medium",
        status=status
    ))
    
    return recommendations

