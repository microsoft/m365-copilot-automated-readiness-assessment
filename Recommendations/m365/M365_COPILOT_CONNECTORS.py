"""
Microsoft 365 Copilot Connectors - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Copilot Connectors enable custom plugins and extensions that connect Copilot
    to line-of-business systems, third-party APIs, and custom enterprise data sources.
    """
    feature_name = "Microsoft 365 Copilot Connectors"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, allowing custom integrations to extend Copilot capabilities",
            recommendation="",
            link_text="Extend Copilot with Plugins",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/extensibility/",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing custom Copilot extensions and integrations",
            recommendation=f"Enable {feature_name} to extend M365 Copilot beyond Microsoft's native capabilities. Build custom plugins that connect Copilot to your CRM, ERP, ticketing systems, and proprietary databases. Create message extensions that let Copilot perform actions (create ServiceNow tickets, update Salesforce records, submit approvals in custom workflows). Connectors transform Copilot from a general assistant into an intelligent interface for your entire technology stack, enabling employees to work with all their tools through natural language.",
            link_text="Extend Copilot with Plugins",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/extensibility/",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
        teams_active_users = m365_insights.get('teams_active_users', 0)        
        # ALWAYS create observation showing connector extensibility potential (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Connector readiness: {total_active_users:,} users, {sharepoint_total_files:,} files, {teams_active_users:,} Teams users. Copilot Connectors ARE the extensibility layer - build custom plugins connecting Copilot to CRM, ERP, ServiceNow, custom databases. Agents can query external systems via natural language. Critical for enterprise AI where 80% of valuable data lives OUTSIDE M365.",
            recommendation="",
            link_text="Build Copilot Plugins",
            link_url="https://learn.microsoft.com/microsoft-365-copilot/extensibility/",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # Enterprise data complexity - strong connector value
        if total_active_users >= 30 and sharepoint_total_files >= 200:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Enterprise scale: {total_active_users:,} users, {sharepoint_total_files:,} files indicate complex data ecosystem likely with multiple LOB systems. Strong connector opportunity.",
                recommendation="Develop custom Copilot connectors for your CRM, ERP, ticketing, and proprietary systems. With {total_active_users:,} users across {sharepoint_total_files:,} files, you have enterprise data sprawl - Connectors unify access via AI. Build plugins for: Salesforce queries, ServiceNow ticket creation, SAP data lookups, custom API calls. Enable Copilot to become single interface for ALL your systems, not just M365.",
                link_text="Connector Development",
                link_url="https://learn.microsoft.com/microsoft-365-copilot/extensibility/build-declarative-agents",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)        
        # Growing complexity - pilot connectors
        elif total_active_users >= 15 or sharepoint_total_files >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing ecosystem: {total_active_users:,} users and {sharepoint_total_files:,} files suggest integration opportunities. Pilot connector use cases.",
                recommendation="Identify 2-3 high-value external systems for Copilot integration pilots. Start with systems your {total_active_users:,} users access frequently - CRM for sales, ticketing for IT, financial systems for finance teams. Build simple connectors (read-only queries first), measure time savings, expand to write operations (create tickets, update records) based on success.",
                link_text="Connector Pilot Guide",
                link_url="https://learn.microsoft.com/microsoft-365-copilot/extensibility/",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    return recommendations
