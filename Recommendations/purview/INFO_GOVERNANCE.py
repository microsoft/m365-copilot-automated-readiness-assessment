"""
Information Governance - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Information Governance applies automated retention and deletion policies
    to content that Copilot accesses and generates across Microsoft 365.
    """
    feature_name = "Information Governance"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, governing the lifecycle of content in Copilot's knowledge base",
            recommendation="",
            link_text="Govern AI Content Lifecycle",
            link_url="https://learn.microsoft.com/purview/information-governance",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, allowing stale or inappropriate content in Copilot responses",
            recommendation=f"Enable {feature_name} to control what content Copilot can access through automated lifecycle policies. Ensure outdated policies, superseded procedures, and obsolete project documentation are deleted rather than surfaced in AI responses. Apply retention labels to Teams chats and emails so Copilot doesn't cite conversations that should have been disposed. Information Governance keeps Copilot's knowledge base current, compliant, and trustworthy by automatically managing content that AI systems reference.",
            link_text="Govern AI Content Lifecycle",
            link_url="https://learn.microsoft.com/purview/information-governance",
            priority="Medium",
            status=status
        )
    
    # Check deployment status from PowerShell data (uses retention labels/policies)
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'retention_labels'):
        labels_data = purview_client.retention_labels
        
        if labels_data.get('available'):
            total_labels = labels_data.get('total_labels', 0)
            labels = labels_data.get('labels', [])
            
            if total_labels > 0:
                label_names = ', '.join([l.get('Name', 'Unnamed') for l in labels[:3]])
                if len(labels) > 3:
                    label_names += f" (+{len(labels)-3} more)"
                
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Retention Strategy",
                    observation=f"{total_labels} retention labels configured: {label_names}",
                    recommendation=f"Ensure retention controls keep Copilot's knowledge base current: 1) Delete obsolete policies/procedures after 2 years (prevent Copilot citing outdated info), 2) Retain Teams meeting transcripts 3 years (preserve Copilot training context), 3) Dispose old project chats after completion (keep AI responses relevant), 4) Permanently delete draft emails (prevent Copilot referencing abandoned content). Configure in Purview > Records management. Currently {total_labels} labels deployed.",
                    link_text="Retention for AI Content",
                    link_url="https://learn.microsoft.com/purview/retention",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Retention Strategy",
                    observation="Information Governance license active but NO retention labels configured",
                    recommendation="Deploy retention labels to control Copilot's content access: 1) Delete policies/procedures older than 2 years (prevent AI citing outdated guidance), 2) Retain meeting transcripts 3 years (preserve decision context), 3) Dispose completed project content 1 year after closure (keep AI focused on current work), 4) Delete draft documents permanently (prevent AI referencing abandoned work). Configure in Purview > Records management.",
                    link_text="Configure Retention",
                    link_url="https://learn.microsoft.com/purview/create-retention-labels",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
