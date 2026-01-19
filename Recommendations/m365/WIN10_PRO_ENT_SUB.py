"""
Windows 10/11 Enterprise - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Windows Enterprise provides the OS platform required for
    Windows Copilot and native AI features integration.
    """
    feature_name = "Windows 10/11 Enterprise"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing the foundation for Windows Copilot integration",
            recommendation="",
            link_text="Windows Enterprise for AI",
            link_url="https://learn.microsoft.com/windows/whats-new/",
            status=status
        ))
        
        if m365_insights and m365_insights.get('available'):
            total_active_users = m365_insights.get('total_active_users', 0)
            
            # ALWAYS create observation showing current metrics (no threshold)
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Current user metrics: {total_active_users:,} active users. Windows 10/11 Enterprise provides Windows Copilot integration and enterprise-grade security for AI workloads across your organization.",
                recommendation="",
                link_text="Windows Enterprise for AI",
                link_url="https://learn.microsoft.com/windows/whats-new/",
                status="Success"
            )
            recommendations.append(obs_rec)
    
    return recommendations
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing enterprise Windows capabilities for Copilot",
        recommendation=f"Enable {feature_name} to provide the enterprise OS platform for Windows Copilot and native AI features. Windows 11 Enterprise includes Windows Copilot for system-wide assistance, Recall for finding past activity (where available), and enhanced security features that protect AI workloads. Enterprise editions provide management capabilities through Intune, ensuring consistent Copilot configuration across devices. Critical for organizations deploying M365 Copilot as it ensures OS-level integration and enterprise-grade security for AI experiences.",
        link_text="Windows Enterprise for AI",
        link_url="https://learn.microsoft.com/windows/whats-new/",
        priority="Medium",
        status=status
    ))
    return recommendations
