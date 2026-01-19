"""
Microsoft Purview eDiscovery - Purview & Compliance Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Microsoft Purview eDiscovery provides advanced eDiscovery capabilities for legal and compliance.
    """
    feature_name = "Microsoft Purview eDiscovery"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling legal hold and eDiscovery of data including Copilot interactions",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}",
            recommendation=f"Enable {feature_name} to search, hold, and export content for legal and compliance investigations.",
            link_text="Purview eDiscovery",
            link_url="https://learn.microsoft.com/purview/ediscovery",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'ediscovery_cases'):
        ediscovery_data = purview_client.ediscovery_cases
        
        if ediscovery_data.get('available'):
            total_cases = ediscovery_data.get('total_cases', 0)
            
            if total_cases > 0:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Active Cases",
                    observation=f"Purview eDiscovery has {total_cases} active case(s) configured - legal hold framework is deployed",
                    recommendation=f"You have {total_cases} active eDiscovery case(s). Ensure cases are configured to capture Copilot-related content for legal holds: 1) Include Teams chats with Copilot interactions in case scope, 2) Preserve OneDrive/SharePoint content accessed via AI assistants, 3) Capture meeting recordings and transcripts that feed Copilot context, 4) Hold documents created or modified through Copilot. During legal discovery, this preserves the full context of how AI was used to access, process, or generate content relevant to litigation. Use Get-ComplianceCase to review active matters and ensure Copilot data sources are included.",
                    link_text="Manage eDiscovery Cases",
                    link_url="https://learn.microsoft.com/purview/ediscovery-cases",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Purview eDiscovery license is active but NO cases are configured",
                    recommendation="Create eDiscovery cases to prepare for legal holds involving Copilot content. Set up cases BEFORE litigation occurs to establish processes for: 1) Preserving Copilot chat histories and AI interactions relevant to legal matters, 2) Searching for documents created or modified via AI assistants during specific timeframes, 3) Exporting meeting transcripts and recordings that provide context for Copilot summaries, 4) Holding content across multiple Microsoft 365 workloads (Teams, OneDrive, SharePoint, Exchange) that Copilot accesses. Configure in Purview compliance portal > eDiscovery > Standard/Premium cases. Define custodians and data sources that include Copilot-enabled locations. Use Get-ComplianceCase to verify setup.",
                    link_text="Create eDiscovery Cases",
                    link_url="https://learn.microsoft.com/purview/ediscovery-standard-get-started",
                    priority="Medium",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
