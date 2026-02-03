"""
Nucleus - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Nucleus is an internal Microsoft component that supports
    various M365 services infrastructure.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Nucleus"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling cross-workload data orchestration that allows Copilot to surface insights across Microsoft Graph from emails, documents, meetings, and chats in a unified intelligence layer",
            recommendation="",
            link_text="Microsoft Graph and Copilot Data Layer",
            link_url="https://learn.microsoft.com/graph/overview",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing core infrastructure components",
            recommendation=f"Enable {feature_name} to provide foundational M365 infrastructure services that support various workloads. Nucleus is typically an internal component included automatically with M365 services rather than a user-facing feature. It provides backend capabilities that other services depend on, potentially including infrastructure for AI and Copilot services. Generally managed automatically as part of the M365 platform rather than requiring specific configuration or enablement.",
            link_text="M365 Core Services",
            link_url="https://learn.microsoft.com/microsoft-365/",
            priority="Low",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
        email_active_users = m365_insights.get('email_active_users', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        total_active_users = m365_insights.get('total_active_users', 0)
        
        # ALWAYS create observation showing current data layer metrics (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Knowledge graph baseline: {sharepoint_total_files:,} SharePoint files, {email_active_users:,} email users, {teams_active_users:,} Teams users. Nucleus (Microsoft Graph) IS Copilot's brain - the unified knowledge graph where agents retrieve documents, traverse relationships, and access organizational context. Every file indexed, every connection mapped, every permission checked flows through Graph. Without Nucleus data richness, Copilot's answers lack depth.",
            recommendation="",
            link_text="AI Knowledge Layer",
            link_url="https://learn.microsoft.com/graph/overview",
            status="Success"
        )
        recommendations.append(obs_rec)
        
        # Rich data layer - Copilot has substantial context
        if sharepoint_total_files >= 500 and email_active_users >= 30:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Rich Microsoft Graph data layer: {sharepoint_total_files:,} files and {email_active_users:,} email users. Nucleus provides Copilot with comprehensive organizational context.",
                recommendation="Leverage this rich data foundation for Copilot deployment. With substantial content in SharePoint and active email communication, Copilot can provide highly contextual responses drawing from organizational knowledge.",
                link_text="Optimize Copilot with Graph Data",
                link_url="https://learn.microsoft.com/graph/overview",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)
        
        # Moderate data - growing foundation
        elif sharepoint_total_files >= 50 or email_active_users >= 10:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing data layer: {sharepoint_total_files:,} SharePoint files and {email_active_users:,} email users. Nucleus orchestrates increasing M365 content for Copilot.",
                recommendation="Continue building Microsoft Graph content through SharePoint, Teams, and email adoption. As data layer grows, Copilot responses become more contextual and valuable.",
                link_text="Build Graph Content Base",
                link_url="https://learn.microsoft.com/graph/overview",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    
    return recommendations
