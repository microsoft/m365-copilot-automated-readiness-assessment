"""
Microsoft Intune Suite - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Intune Suite provides advanced endpoint management capabilities
    that ensure secure device configuration for Copilot usage.
    """
    feature_name = "Microsoft Intune Suite"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing advanced endpoint management for secure Copilot deployment",
            recommendation="",
            link_text="Secure Endpoint Management for AI",
            link_url="https://learn.microsoft.com/mem/intune/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, lacking advanced endpoint security controls",
            recommendation=f"Enable {feature_name} to deploy advanced endpoint management capabilities including specialized security, remote help, and endpoint privilege management. Intune Suite ensures devices accessing Copilot meet security baselines, enforces conditional access policies based on device compliance, and provides remote assistance for Copilot troubleshooting. Use endpoint analytics to identify device performance issues affecting Copilot experience and automate remediation. Critical for zero-trust security posture when deploying AI to managed and BYOD devices.",
            link_text="Secure Endpoint Management for AI",
            link_url="https://learn.microsoft.com/mem/intune/",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Endpoint security: {total_active_users:,} users. Intune Suite provides advanced endpoint management for secure Copilot deployment - device compliance, conditional access, remote troubleshooting. Ensures devices meet security baselines before accessing AI. Critical for zero-trust posture with managed and BYOD devices.",
            recommendation="",
            link_text="Intune Suite Security",
            link_url="https://learn.microsoft.com/mem/intune/",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        if total_active_users >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Device management scale: {total_active_users:,} users require comprehensive endpoint security for Copilot access.",
                recommendation="Deploy Intune Suite advanced features for your {total_active_users:,} users: endpoint analytics for Copilot performance monitoring, remote help for AI troubleshooting, privilege management for secure access. Ensure all devices meet compliance baselines before Copilot enablement.",
                link_text="Intune Suite Deployment",
                link_url="https://learn.microsoft.com/mem/intune/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
