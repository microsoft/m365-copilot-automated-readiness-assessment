"""
Sway - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", m365_insights=None):
    """
    Sway enables creating interactive reports and presentations that
    Copilot can generate from existing content and data.
    """
    feature_name = "Sway"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-generated interactive content",
            recommendation="",
            link_text="Create Sways with Copilot",
            link_url="https://learn.microsoft.com/sway/",
            status=status
        ))
    else:
        recommendations.append(new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting AI content creation options",
            recommendation=f"Enable {feature_name} to let Copilot create visually appealing, web-based presentations and reports. Use AI to generate Sways from meeting notes, transform document content into interactive newsletters, and create data stories from Excel analytics. Sway provides an alternative to PowerPoint for scenarios where web-native, responsive content is more appropriate, particularly for internal communications and knowledge sharing that Copilot can automate.",
            link_text="Create Sways with Copilot",
            link_url="https://learn.microsoft.com/sway/",
            priority="Low",
            status=status
        ))
    
    # NEW: Usage Context based on SharePoint files and active users
    if status == "Success" and m365_insights and m365_insights.get('sharepoint_report_available'):
        total_files = m365_insights.get('total_files', 0)
        active_users = m365_insights.get('sharepoint_active_users', 0)
        
        if total_files >= 1000 and active_users >= 100:
            # High content + users = strong case for Sway content creation
            recommendations.append(new_recommendation(
                service="M365",
                feature="Sway",
                observation=f"Your tenant has {total_files} SharePoint files and {active_users} active SharePoint users. This content-rich environment creates opportunities for Sway to transform existing documents into engaging, web-based presentations and newsletters, enhancing internal communications and knowledge sharing.",
                recommendation="",  # No recommendation - this is helpful context
                link_text="",
                link_url="",
                priority="",
                status=""
            ))
        elif total_files >= 500 or active_users >= 50:
            # Moderate content = suggest Sway for specific use cases
            recommendations.append(new_recommendation(
                service="M365",
                feature="Sway",
                observation=f"Your tenant has {total_files} SharePoint files and {active_users} active SharePoint users. Consider using Sway for internal communications, project updates, or knowledge base articles where web-native, visually appealing content would improve engagement over traditional documents.",
                recommendation=f"Pilot Sway for internal communications. With {total_files} SharePoint files, you have content that could be transformed into interactive Sways for newsletters, project showcases, or onboarding materials. Start with communications or HR teams to create web-based content that's more engaging than static documents, particularly for mobile users.",
                link_text="Create Your First Sway",
                link_url="https://support.microsoft.com/sway",
                priority="Low",
                status="PendingInput"
            ))
        else:
            # Low content/users = focus on core content creation first
            recommendations.append(new_recommendation(
                service="M365",
                feature="Sway",
                observation=f"Your tenant has {total_files} SharePoint files and {active_users} active SharePoint users. Focus on building SharePoint content base for Copilot knowledge grounding before investing in Sway - agents need rich document repositories to provide intelligent recommendations.",
                recommendation=f"Build core content foundation before deploying Sway. With {total_files} SharePoint files and {active_users} active users, prioritize creating structured content in SharePoint, Teams, and OneDrive first. Once your content base grows, then leverage Sway for specific use cases like executive updates or marketing materials where visual presentation is critical.",
                link_text="SharePoint Content Planning",
                link_url="https://learn.microsoft.com/sharepoint/plan-site-architecture",
                priority="Low",
                status="PendingInput"
            ))

    return recommendations
