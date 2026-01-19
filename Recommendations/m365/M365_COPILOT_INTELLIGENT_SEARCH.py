"""
Microsoft 365 Copilot - Intelligent Search - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Intelligent Search powers Copilot's ability to find and surface relevant information
    across Microsoft 365 using semantic understanding and AI-enhanced indexing.
    """
    feature_name = "Microsoft 365 Copilot - Intelligent Search"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []    
    # DEBUG: Log insights availability    
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling semantic search and intelligent content discovery for Copilot",
            recommendation="",
            link_text="AI-Powered Search in Microsoft 365",
            link_url="https://learn.microsoft.com/microsoftsearch/overview-microsoft-search",
            status=status
        )
        recommendations.append(license_rec)
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, degrading Copilot's ability to find relevant information",
            recommendation=f"Enable {feature_name} to power Copilot's understanding of your organizational content. Intelligent Search uses AI to understand the meaning and context of documents, not just keywords, allowing Copilot to find relevant information even when queries don't match exact terms. It indexes people, files, conversations, and organizational structure to provide personalized, permission-aware results. Without this, Copilot cannot effectively answer questions or generate content based on your organization's specific knowledge, severely limiting its value.",
            link_text="AI-Powered Search in Microsoft 365",
            link_url="https://learn.microsoft.com/microsoftsearch/overview-microsoft-search",
            priority="High",
            status=status
        )
        recommendations.append(license_rec)
    
    # M365 Insights-based Observations
    if status == "Success" and m365_insights and m365_insights.get('available'):
        total_active_users = m365_insights.get('total_active_users', 0)
        sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
        sharepoint_total_sites = m365_insights.get('sharepoint_total_sites', 0)        
        # ALWAYS create observation showing intelligent search context (no threshold)
        obs_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"Search index: {total_active_users:,} users, {sharepoint_total_files:,} files, {sharepoint_total_sites:,} sites. Intelligent Search IS Copilot's brain - semantic indexing across ALL your content, not keyword matching. AI understands meaning, context, relationships between documents. The MORE content ({sharepoint_total_files:,} files), the SMARTER Copilot's answers. Foundation for Business Chat, file summarization, and cross-app AI.",
            recommendation="",
            link_text="Microsoft Search AI",
            link_url="https://learn.microsoft.com/microsoftsearch/overview-microsoft-search",
            status="Success"
        )
        recommendations.append(obs_rec)        
        # Rich content - intelligent search critical
        if sharepoint_total_files >= 200:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Large knowledge base: {sharepoint_total_files:,} files across {sharepoint_total_sites:,} sites create massive semantic search value. AI indexing essential.",
                recommendation="Optimize Intelligent Search for your {sharepoint_total_files:,} files - ensure metadata, topics, and bookmarks are configured. With this content volume, semantic search is transformative: 'Find documents about Q1 strategy' surfaces relevant files even without exact phrase matches. Monitor search analytics to identify knowledge gaps, tune result quality, and promote high-value content.",
                link_text="Search Analytics",
                link_url="https://learn.microsoft.com/microsoftsearch/usage-reports",
                priority="High",
                status="Insight"
            )
            recommendations.append(rec)        
        # Growing content - pilot search features
        elif sharepoint_total_files >= 50:
            rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Growing repository: {sharepoint_total_files:,} files provide solid search foundation. Configure intelligent search features.",
                recommendation="Start configuring Intelligent Search features for your {sharepoint_total_files:,} files: set up topics (automatic subject identification), create bookmarks (promoted answers for common queries), configure result types (enhanced display for specific content). As content grows, these AI features become increasingly valuable for knowledge discovery.",
                link_text="Configure Search",
                link_url="https://learn.microsoft.com/microsoftsearch/overview-microsoft-search",
                priority="Medium",
                status="Insight"
            )
            recommendations.append(rec)
    return recommendations
