"""
Records Management - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Records Management applies retention policies to Copilot-generated content,
    ensuring AI outputs comply with legal hold and regulatory requirements.
    """
    feature_name = "Records Management"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, managing retention of AI-generated records and compliance",
            recommendation="",
            link_text="Retain Copilot Content for Compliance",
            link_url="https://learn.microsoft.com/purview/records-management",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, risking non-compliance with AI content retention requirements",
            recommendation=f"Enable {feature_name} to ensure Copilot-generated documents, meeting summaries, and agent responses are properly retained or disposed according to record schedules. Declare AI-created contracts, financial summaries, and compliance documentation as official records with appropriate legal holds. Track the lifecycle of Copilot outputs that may become evidence in litigation. Without proper records management, organizations face regulatory risk from AI-generated content that should be preserved but gets deleted, or personal data that should be deleted but persists.",
            link_text="Retain Copilot Content for Compliance",
            link_url="https://learn.microsoft.com/purview/records-management",
            priority="Medium",
            status=status
        )
    
    # Check retention policies from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'retention_labels'):
        retention_data = purview_client.retention_labels
        
        if retention_data.get('available'):
            total_labels = retention_data.get('total_labels', 0)
            
            if total_labels > 0:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Retention Labels",
                    observation=f"{total_labels} retention labels configured for records management",
                    recommendation=f"Ensure retention labels cover Copilot-generated content: 1) Meeting transcripts/summaries (retain per communication policy), 2) AI-drafted contracts/agreements (legal retention period), 3) Financial summaries from Copilot (regulatory retention), 4) Compliance documentation (permanent retention). Apply labels automatically to: OneNote pages with Copilot meeting notes, Word docs created with Copilot drafting, emails with AI-generated content. Test: create Copilot content > verify label auto-applies > confirm retention enforced.",
                    link_text="Retention Labels for AI Content",
                    link_url="https://learn.microsoft.com/purview/retention",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Retention Labels",
                    observation="Records Management license active but NO retention labels configured - AI content unmanaged",
                    recommendation="Deploy retention labels for Copilot-generated records: 1) Meeting Records (retain 7 years) - auto-label Teams meeting transcripts, 2) Contracts (retain 10 years) - apply to Word docs with Copilot contract drafting, 3) Financial Records (regulatory retention) - label Excel/PowerPoint with financial Copilot summaries, 4) Compliance Documentation (permanent). Without labels, AI-generated business records may be prematurely deleted, creating legal/regulatory risk. Configure in Purview > Records management > File plan.",
                    link_text="Configure Retention Labels",
                    link_url="https://learn.microsoft.com/purview/file-plan-manager",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
