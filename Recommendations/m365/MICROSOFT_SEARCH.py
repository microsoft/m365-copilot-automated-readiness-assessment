"""
Microsoft Search - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Microsoft Search provides the enterprise search engine that
    Copilot uses to find and surface relevant information.
    """
    feature_name = "Microsoft Search (Service)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, powering Copilot's information retrieval across M365",
            recommendation="",
            link_text="Enterprise Search for AI",
            link_url="https://learn.microsoft.com/microsoftsearch/",
            status=status
        ))
        
        # M365 Insights - Search foundation for Copilot
        if m365_insights and m365_insights.get('available'):
            sharepoint_total_files = m365_insights.get('sharepoint_total_files', 0)
            email_active_users = m365_insights.get('email_active_users', 0)
            
            # Always create observation with current metrics
            obs_rec = new_recommendation(
                service="M365",
                feature=feature_name,
                observation=f"Search index contains {sharepoint_total_files} SharePoint files and {email_active_users} active email users. Microsoft Search indexes this content for Copilot queries.",
                recommendation="",
                link_text="Enterprise Search",
                link_url="https://learn.microsoft.com/microsoftsearch/",
                status="Success"
            )
            recommendations.append(obs_rec)
        
        return recommendations
    
    
    recommendations.append(new_recommendation(
        service="M365",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, limiting Copilot's ability to find information",
        recommendation=f"Enable {feature_name} to provide the search infrastructure that Copilot relies on for finding relevant content. Microsoft Search indexes emails, documents, sites, and conversations, enabling Copilot to answer questions by retrieving the most relevant information. Without robust search, Copilot cannot effectively ground responses in organizational knowledge, severely limiting its value. Search is the foundation that makes Copilot's answers accurate, contextual, and trustworthy.",
        link_text="Enterprise Search for AI",
        link_url="https://learn.microsoft.com/microsoftsearch/",
        priority="High",
        status=status
    ))
    
    return recommendations
