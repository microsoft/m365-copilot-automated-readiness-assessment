"""
Azure Information Protection Premium P2 - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Azure Information Protection P2 provides automatic classification
    and advanced protection for Copilot-processed sensitive content.
    """
    feature_name = "Azure Information Protection Premium P2"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling automatic classification of Copilot-generated content",
            recommendation="",
            link_text="Advanced Protection for AI Content",
            link_url="https://learn.microsoft.com/azure/information-protection/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing automatic classification for AI workflows",
            recommendation=f"Enable {feature_name} to automatically classify and protect content that Copilot creates or accesses. AIP P2 applies labels based on content inspection (keywords, patterns, regex), ensuring Copilot-generated summaries of confidential documents inherit appropriate protections automatically. Use advanced conditions to detect when Copilot responses contain PII, financial data, or trade secrets, triggering automatic encryption and access controls. P2's automatic classification prevents data exposure when users share AI outputs without realizing sensitivity.",
            link_text="Advanced Protection for AI Content",
            link_url="https://learn.microsoft.com/azure/information-protection/",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data (same as P1 - uses sensitivity labels)
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'sensitivity_labels'):
        labels_data = purview_client.sensitivity_labels
        
        if labels_data.get('available'):
            total_labels = labels_data.get('total_labels', 0)
            labels = labels_data.get('labels', [])
            
            if total_labels > 0:
                label_names = ', '.join([l.get('Name', 'Unnamed') for l in labels[:3]])
                if len(labels) > 3:
                    label_names += f" (+{len(labels)-3} more)"
                
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Auto-Classification",
                    observation=f"{total_labels} sensitivity labels available for auto-classification: {label_names}",
                    recommendation=f"Configure automatic labeling conditions for Copilot scenarios: 1) Auto-label documents containing PII patterns (SSN, credit cards) that Copilot summarizes, 2) Apply 'Confidential' to AI responses containing financial keywords, 3) Detect trade secret terminology in Copilot outputs, 4) Automatically encrypt content with customer data patterns. AIP P2 prevents data leaks when users copy/share Copilot responses without realizing sensitivity. Configure in Purview > Information protection > Auto-labeling. Currently {total_labels} labels deployed.",
                    link_text="Auto-Labeling for AI Content",
                    link_url="https://learn.microsoft.com/purview/apply-sensitivity-label-automatically",
                    priority="Medium",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Auto-Classification",
                    observation="Azure Information Protection P2 license active but NO sensitivity labels configured for auto-classification",
                    recommendation="Deploy sensitivity labels with automatic classification rules: 1) Confidential (auto-detect PII in Copilot responses), 2) Financial (keyword-based detection in AI summaries), 3) Trade Secrets (pattern matching for proprietary info), 4) Customer Data (regex for customer identifiers). Without auto-labeling, users manually classify Copilot outputs - often incorrectly. Configure in Purview > Information protection > Auto-labeling.",
                    link_text="Configure Auto-Labeling",
                    link_url="https://learn.microsoft.com/purview/apply-sensitivity-label-automatically",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
