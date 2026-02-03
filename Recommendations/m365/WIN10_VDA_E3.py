"""
Windows 10/11 Enterprise E3 - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Windows 10/11 Enterprise E3 provides enterprise OS features
    that support Windows Copilot integration and security.
    """
    recommendations = []
    
    feature_name = "Windows 10/11 Enterprise E3"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing enterprise OS for Windows Copilot and AI-powered features",
            recommendation="",
            link_text="Enterprise Windows Features",
            link_url="https://learn.microsoft.com/windows/whats-new/copilot/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing enterprise OS capabilities for Windows Copilot",
            recommendation=f"Enable {feature_name} to provide Windows 10/11 Enterprise licensing required for Windows Copilot and advanced AI features. Enterprise edition includes security capabilities that protect Copilot interactions, BitLocker encryption for AI-generated content, and Windows Hello for secure authentication to AI services. Enterprise features enable centralized policy management for Copilot settings, ensuring compliance with data governance requirements. Essential foundation for device-level AI integration, Windows Copilot assistance, and secure access to cloud-based M365 Copilot services from managed devices.",
            link_text="Enterprise Windows Features",
            link_url="https://learn.microsoft.com/windows/whats-new/copilot/",
            priority="Medium",
            status=status
        ))
    
    # M365 Insights - Windows Enterprise Copilot Foundation
    if m365_insights:
        total_active_users = m365_insights.get('total_active_users', 0)
        
        # Baseline observation - always created when insights available
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Windows Enterprise E3 provides foundational OS licensing for Windows Copilot integration - built-in OS-level AI assistant, taskbar Copilot access, integration with M365 services. Enterprise features critical for Copilot security: BitLocker encrypts AI-generated content, Windows Hello secures authentication to AI services, Group Policy manages Copilot settings at scale. Device management via Intune enables centralized control: which users access Windows Copilot, data governance policies, compliance requirements. Essential infrastructure layer beneath M365 Copilot - secure managed devices are prerequisite for enterprise AI deployment.",
            recommendation="",
            link_text="Windows Copilot Foundation",
            link_url="https://learn.microsoft.com/windows/whats-new/copilot/",
            status="Success"
        ))
        
        # Threshold-based recommendation
        if total_active_users >= 200:
            recommendations.append(new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"With {total_active_users} users, Windows Enterprise E3 provides managed device foundation for Windows Copilot OS integration and M365 Copilot security",
                recommendation=f"Deploy Windows Enterprise E3 for your {total_active_users} users to enable Windows Copilot OS-level integration and secure M365 Copilot access. Use Group Policy and Intune to configure Copilot settings at scale: enable/disable Windows Copilot per user role, enforce data protection policies for AI-generated content, ensure BitLocker encryption on devices accessing sensitive AI services. Enterprise management critical for Copilot governance - control which users leverage AI, monitor compliance, audit AI interactions.",
                link_text="Enterprise Copilot Deployment",
                link_url="https://learn.microsoft.com/windows/whats-new/copilot/",
                status="Insight",
                priority="Medium"
            ))
    
    return recommendations
