"""
Azure Information Protection Premium P1 - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Azure Information Protection P1 provides classification and labeling
    that informs Copilot's handling of sensitive information.
    """
    feature_name = "Azure Information Protection Premium P1"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling label-aware Copilot operations on classified content",
            recommendation="",
            link_text="Information Protection for AI",
            link_url="https://learn.microsoft.com/azure/information-protection/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing classification controls for AI content handling",
            recommendation=f"Enable {feature_name} to apply sensitivity labels that govern how Copilot handles information. AIP P1 allows manual and recommended labeling, ensuring Copilot respects data classification when summarizing documents, generating content, or sharing information. Labels can restrict whether Copilot can include labeled content in responses, prevent AI from processing highly confidential data, and enforce encryption on Copilot-generated outputs containing sensitive information. Essential for compliance-conscious Copilot adoption.",
            link_text="Information Protection for AI",
            link_url="https://learn.microsoft.com/azure/information-protection/",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
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
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"{total_labels} sensitivity labels configured: {label_names}",
                    recommendation=f"Verify labels control Copilot behavior: 1) Confidential labels should prevent AI from including content in responses, 2) Public labels allow Copilot summarization, 3) Internal labels restrict sharing outside organization, 4) Highly Confidential labels enforce encryption on AI-generated outputs. Test in Copilot: Ask it to summarize a labeled document - it should respect restrictions. Review in Purview > Information protection > Labels. Currently {total_labels} labels deployed.",
                    link_text="Sensitivity Labels for AI",
                    link_url="https://learn.microsoft.com/purview/sensitivity-labels",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation="Azure Information Protection P1 license active but NO sensitivity labels configured",
                    recommendation="Deploy sensitivity labels to control Copilot's handling of classified content: 1) Confidential (restrict AI summarization), 2) Internal (allow internal AI use only), 3) Public (full AI access), 4) Highly Confidential (encryption required). Without labels, Copilot treats all content equally, potentially exposing sensitive data through AI responses. Configure in Purview > Information protection.",
                    link_text="Create Sensitivity Labels",
                    link_url="https://learn.microsoft.com/purview/create-sensitivity-labels",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
