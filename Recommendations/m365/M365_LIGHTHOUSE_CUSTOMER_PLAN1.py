"""
Microsoft 365 Lighthouse - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft 365 Lighthouse provides multi-tenant management for
    MSPs managing Copilot deployments across client organizations.
    """
    feature_name = "Microsoft 365 Lighthouse"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, allowing MSP partners to monitor this tenant's security posture, compliance baselines, and user management through centralized oversight—foundational requirements for successful Copilot deployment",
            recommendation="",
            link_text="MSP Multi-Tenant Management",
            link_url="https://learn.microsoft.com/microsoft-365/lighthouse/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting multi-tenant management capabilities",
            recommendation=f"Enable {feature_name} for Managed Service Providers overseeing Copilot deployments across multiple client organizations. Lighthouse provides centralized visibility into security baselines, compliance status, and deployment health across all managed tenants. Monitor Copilot adoption rates, identify security gaps in AI configurations, and deploy consistent policies at scale. Essential for MSPs offering Copilot managed services, enabling efficient oversight without individual tenant logins while maintaining security and compliance across the customer portfolio.",
            link_text="Multi-Tenant Copilot Management",
            link_url="https://learn.microsoft.com/microsoft-365/lighthouse/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)        
        # ALWAYS create observation showing Lighthouse management context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"MSP management: {total_active_users:,} users under Lighthouse oversight. M365 Lighthouse IS the MSP platform for managing Copilot deployments across client tenants - centralized security baselines, compliance monitoring, deployment health, adoption tracking. MSPs use Lighthouse to ensure AI governance, monitor security posture, and track Copilot ROI across their customer portfolio without per-tenant logins.",
            recommendation="",
            link_text="Lighthouse Copilot Management",
            link_url="https://learn.microsoft.com/microsoft-365/lighthouse/",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # Note: Lighthouse is MSP management tool - thresholds less relevant than other Copilot features
        # No usage-based recommendations as this is administrative/management capability, not end-user feature    
    return recommendations
