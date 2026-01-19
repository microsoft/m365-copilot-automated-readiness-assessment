"""
Information Protection for Office 365 - Premium - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Premium Information Protection enables automatic sensitivity labeling on
    AI-generated content and enforces DLP policies on Copilot interactions.
    Returns 2 recommendations: license status + label deployment status.
    """
    feature_name = "Information Protection for Office 365 - Premium"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, automatically labeling content created and accessed by Copilot",
            recommendation="",
            link_text="Automatic AI Content Protection",
            link_url="https://learn.microsoft.com/purview/information-protection",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing automatic classification of Copilot-generated content",
            recommendation=f"Enable {feature_name} to automatically apply sensitivity labels to documents created by M365 Copilot, emails drafted through AI assistance, and summaries generated from sensitive sources. Trainable classifiers can identify when Copilot outputs contain confidential information (financial data, customer PII, legal documents), ensuring AI-created content receives appropriate protection without relying on user vigilance. Auto-labeling prevents data leaks through careless prompting where users ask Copilot to process sensitive data without applying labels. Essential for enterprises where Copilot adoption must align with compliance requirements and data governance policies.",
            link_text="Automatic AI Content Protection",
            link_url="https://learn.microsoft.com/purview/information-protection",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'sensitivity_labels'):
        label_data = purview_client.sensitivity_labels
        
        if label_data.get('available'):
            total_labels = label_data.get('total_labels', 0)
        
            if total_labels >= 4:
                # Good label deployment (standard baseline is 4+ labels)
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"{total_labels} sensitivity labels configured, enabling automatic classification of Copilot-generated content",
                    recommendation="Configure auto-labeling policies in Microsoft Purview for Copilot scenarios: 1) Auto-label documents containing financial data patterns when created via Copilot in Excel/Word, 2) Auto-apply 'Confidential' to emails drafted by Copilot that mention customer names or account numbers, 3) Use trainable classifiers to detect when Copilot summaries contain sensitive content types (legal, HR, M&A), 4) Set default label to 'General' for all Copilot outputs unless higher sensitivity detected. Test by asking Copilot to create document with financial data - verify auto-labeling applies correct classification. Use Get-Label to review deployed labels.",
                    link_text="Auto-Labeling for AI Content",
                    link_url="https://learn.microsoft.com/purview/apply-sensitivity-label-automatically",
                    priority="Medium",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            elif total_labels >= 1:
                # Minimal labels deployed
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"Only {total_labels} sensitivity label(s) configured, limiting automatic classification granularity for Copilot outputs",
                    recommendation=f"Expand sensitivity label taxonomy from {total_labels} to at least 4 labels for effective auto-labeling: 'Public' (Copilot outputs safe for external sharing), 'General/Internal' (default for most AI-generated content), 'Confidential' (Copilot summaries of sensitive business data), 'Highly Confidential' (AI outputs involving executive/financial/HR content). Premium's auto-labeling requires sufficient label granularity to accurately classify Copilot-generated content. With only {total_labels} label(s), auto-classification cannot distinguish sensitivity levels, reducing protection effectiveness. Deploy complete label taxonomy before enabling auto-labeling policies. Use Get-Label to review current labels.",
                    link_text="Auto-Labeling Configuration",
                    link_url="https://learn.microsoft.com/purview/apply-sensitivity-label-automatically",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                # No labels published
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"Information Protection Premium active but NO sensitivity labels configured - auto-labeling cannot function",
                    recommendation=f"Immediately create and publish sensitivity labels - Premium's auto-labeling is useless without labels to apply. Deploy 4 baseline labels: 'Public', 'General', 'Confidential', 'Highly Confidential'. Then configure auto-labeling policies for Copilot outputs: detect financial patterns (credit cards, account numbers) → auto-apply 'Confidential', detect PII (SSN, passport numbers) → 'Highly Confidential', use trainable classifiers for industry-specific content. Without labels, Premium cannot automatically protect Copilot-generated content containing sensitive data. This creates significant data leak risk as users rely on AI to process confidential information. Deploy labels NOW. Use Get-Label to verify setup.",
                    link_text="Create Labels for Auto-Classification",
                    link_url="https://learn.microsoft.com/purview/create-sensitivity-labels",
                    priority="Critical",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
