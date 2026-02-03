"""
Microsoft Places (Core) - M365 & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Places (Core) coordinates hybrid work and in-person collaboration.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft Places (Core)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    recommendations = []
    
    # License Status Recommendation
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling workplace coordination that agents can query and manage",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to coordinate hybrid work locations and optimize office space usage.",
            link_text="Microsoft Places Overview",
            link_url="https://learn.microsoft.com/microsoft-365/places/overview",
            priority="Medium",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        # Use active users and meeting patterns as proxy for hybrid work coordination need
        total_active_users = m365_insights.get('total_active_users', 0)
        teams_total_meetings = m365_insights.get('teams_total_meetings', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)
        
        
        # Large distributed workforce - critical for hybrid coordination
        if total_active_users >= 500:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large distributed workforce of {total_active_users} active users with {teams_total_meetings} virtual meetings. Microsoft Places can coordinate in-person collaboration and optimize office space for hybrid teams.",
                recommendation="",
                link_text="Microsoft Places Overview",
                link_url="https://learn.microsoft.com/microsoft-365/places/overview",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        # Medium workforce - valuable for hybrid coordination
        elif total_active_users >= 100:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Medium-sized workforce of {total_active_users} active users. Microsoft Places can help coordinate who's working from office vs. home, optimizing in-person collaboration opportunities.",
                recommendation="Deploy Microsoft Places to enable employees to see when teammates plan to be in office. Coordinate in-person days for team meetings and collaboration, reducing wasted office visits when key colleagues are remote.",
                link_text="Microsoft Places Overview",
                link_url="https://learn.microsoft.com/microsoft-365/places/overview",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
        
        # Smaller workforce - establish hybrid work coordination
        else:
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Smaller workforce of {total_active_users} active users. Microsoft Places can establish hybrid work coordination patterns essential for Copilot-powered space booking and team presence awareness as organization scales.",
                recommendation="Implement Microsoft Places early to build hybrid work coordination culture. Even small teams benefit from knowing when colleagues plan office visits, enabling purposeful in-person collaboration rather than random office attendance.",
                link_text="Microsoft Places Overview",
                link_url="https://learn.microsoft.com/microsoft-365/places/overview",
                priority="Low",
                status="Insight"
            )
            recommendations.append(obs_rec)
    return recommendations
