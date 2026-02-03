"""
eDiscovery Analytics - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    eDiscovery Analytics uses AI to analyze Copilot conversation history,
    meeting summaries, and agent interactions for legal discovery.
    """
    feature_name = "eDiscovery Analytics"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling AI-powered legal discovery including Copilot content",
            recommendation="",
            link_text="eDiscovery for AI Interactions",
            link_url="https://learn.microsoft.com/purview/ediscovery",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
                observation=f"{feature_name} is {status} in {friendly_sku}, complicating legal discovery of AI-generated content",
            recommendation=f"Enable {feature_name} to apply machine learning to eDiscovery that includes Copilot and agent content. Use AI to identify relevant Copilot meeting summaries, classify agent conversations by topic, detect near-duplicate AI-generated documents, and analyze themes in how employees used Copilot around litigation matters. eDiscovery Analytics makes it feasible to handle the volume of AI-related content in legal holds while reducing review costs through intelligent prioritization.",
            link_text="eDiscovery for AI Interactions",
            link_url="https://learn.microsoft.com/purview/ediscovery",
            priority="Medium",
            status=status
        )
    
    # Check deployment status from PowerShell data (uses eDiscovery cases data)
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'ediscovery_cases'):
        case_data = purview_client.ediscovery_cases
        
        # Generate recommendation whether data is available or not (0 count = not configured)
        total_cases = case_data.get('total_cases', 0)
        active_cases = case_data.get('active_cases', 0)
        
        if total_cases > 0:
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Analytics Usage",
                    observation=f"{total_cases} eDiscovery cases configured ({active_cases} active) - Analytics available for review",
                    recommendation=f"Use eDiscovery Analytics on Copilot content: 1) Apply themes to categorize Copilot meeting summaries by topic, 2) Use near-duplicate detection on AI-generated reports, 3) Analyze email threads that reference Copilot outputs, 4) Identify key custodians based on Copilot usage patterns. This reduces manual review time when AI content is part of legal discovery. Review in Purview > eDiscovery > Premium > Analytics.",
                    link_text="eDiscovery Analytics",
                    link_url="https://learn.microsoft.com/purview/ediscovery-analyze-data-in-review-set",
                    priority="Low",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
        else:
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Analytics Usage",
                    observation="eDiscovery Analytics license active but NO eDiscovery cases configured",
                    recommendation="Create eDiscovery cases to preserve Copilot-related content for legal discovery: 1) Place custodians on hold to preserve their Copilot chat history, 2) Search for Teams meeting transcripts analyzed by Copilot, 3) Identify documents created/edited with AI assistance. Use Analytics to find relevant AI interactions faster. Configure in Purview > eDiscovery.",
                    link_text="Create eDiscovery Cases",
                    link_url="https://learn.microsoft.com/purview/ediscovery-create-and-manage-cases",
                    priority="Medium",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
