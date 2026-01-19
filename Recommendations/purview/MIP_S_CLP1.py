"""
Information Protection for Office 365 - Standard - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """
    Check information protection label deployment and configuration.
    Returns dict with label details.
    """
    try:
        # Get sensitivity labels from Information Protection
        labels_response = await client.information_protection.policy.labels.get()
        
        if not labels_response or not labels_response.value:
            return {
                'available': False,
                'total_labels': 0,
                'published_labels': 0
            }
        
        total_labels = len(labels_response.value)
        published_labels = sum(1 for label in labels_response.value if hasattr(label, 'is_enabled') and label.is_enabled)
        
        # Get label names for reporting
        label_names = [label.name for label in labels_response.value if hasattr(label, 'name') and label.name][:5]  # First 5
        
        return {
            'available': True,
            'total_labels': total_labels,
            'published_labels': published_labels,
            'label_names': label_names
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        if '401' in error_msg or 'unauthorized' in error_msg:
            return {
                'available': False,
                'error': 'insufficient_permissions',
                'message': 'InformationProtectionPolicy.Read permission required'
            }
        elif '403' in error_msg or 'forbidden' in error_msg:
            return {
                'available': False,
                'error': 'access_denied',
                'message': 'Admin consent required for InformationProtectionPolicy.Read'
            }
        return {
            'available': False,
            'error': 'unknown',
            'message': f'Unable to check label deployment: {str(e)}'
        }

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Information Protection Standard provides basic sensitivity labels
    that guide Copilot's handling of classified content.
    Returns 2+ recommendations: license status + label deployment status.
    """
    feature_name = "Information Protection for Office 365 - Standard"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling basic sensitivity labeling for Copilot content",
            recommendation="",
            link_text="Basic Information Protection",
            link_url="https://learn.microsoft.com/purview/information-protection/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, lacking basic content classification controls",
            recommendation=f"Enable {feature_name} to apply manual sensitivity labels to documents and emails that Copilot processes. Standard protection provides the foundation for data classification, allowing users to mark content as Public, Internal, Confidential, or Highly Confidential. While labels are manually applied (unlike Premium's automatic classification), they inform Copilot's behavior when summarizing or sharing labeled content. Standard is the minimum protection level recommended for organizations starting Copilot adoption, with Premium recommended for automated enforcement.",
            link_text="Basic Information Protection",
            link_url="https://learn.microsoft.com/purview/information-protection/",
            priority="Medium",
            status=status
        )
    
    # Collect deployment recommendations
    deployment_recs = []
    
    # Prioritize PowerShell data (more accurate than Graph API)
    if status == "Success" and purview_client and hasattr(purview_client, 'sensitivity_labels'):
        labels_data = purview_client.sensitivity_labels
        label_policies_data = purview_client.label_policies if hasattr(purview_client, 'label_policies') else {'available': False}
        
        if labels_data.get('available'):
            total_labels = labels_data.get('total_labels', 0)
            labels = labels_data.get('labels', [])
            
            # Check label policies
            total_policies = label_policies_data.get('total_policies', 0) if label_policies_data.get('available') else 0
            
            if total_labels >= 4:
                # Good label deployment
                label_names = ', '.join([l.get('DisplayName', l.get('Name', 'Unnamed')) for l in labels[:4]])
                if len(labels) > 4:
                    label_names += f" (+{len(labels)-4} more)"
                
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"{total_labels} sensitivity labels configured ({total_policies} policies): {label_names}",
                    recommendation=f"Verify labels cover Copilot scenarios: 1) Test: label document 'Confidential' > ask Copilot to summarize > attempt external sharing (should block/warn), 2) Set default label policy ('General' or 'Internal Only') for all users, 3) Enable mandatory labeling for sensitive locations (Finance, HR, Legal OneDrive/SharePoint), 4) Train users: Copilot respects label restrictions when sharing AI-generated content. Currently {total_policies} label policies deployed.",
                    link_text="Sensitivity Label Best Practices",
                    link_url="https://learn.microsoft.com/purview/information-protection-deployment",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            elif total_labels >= 1:
                # Minimal labels
                label_names = ', '.join([l.get('DisplayName', l.get('Name', 'Unnamed')) for l in labels])
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"Only {total_labels} sensitivity label(s) configured: {label_names} - insufficient granularity for Copilot protection",
                    recommendation=f"Expand from {total_labels} to minimum 4 labels: 'Public' (external), 'General' (default internal), 'Confidential' (sensitive), 'Highly Confidential' (regulated). Without granular labels, users cannot properly classify content for Copilot - everything is treated equally. Deploy comprehensive taxonomy in Purview > Information protection > Labels.",
                    link_text="Create Sensitivity Labels",
                    link_url="https://learn.microsoft.com/purview/create-sensitivity-labels",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                # No labels
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation="Information Protection license active but ZERO sensitivity labels configured - no content classification",
                    recommendation="Deploy sensitivity labels IMMEDIATELY before Copilot rollout. Create 4 baseline labels: 1) Public (marketing, public docs), 2) General (default for all internal content), 3) Confidential (customer data, contracts, roadmaps), 4) Highly Confidential (financials, M&A, HR). Without labels, Copilot has no protection boundaries - all content treated equally. Configure in Purview > Information protection > Labels, publish to all users.",
                    link_text="Create Sensitivity Labels",
                    link_url="https://learn.microsoft.com/purview/create-sensitivity-labels",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    # Fallback to Graph API if PowerShell data unavailable
    elif status == "Success" and client:
        deployment = await get_deployment_status(client)
        
        if deployment.get('available'):
            total_labels = deployment.get('total_labels', 0)
            published_labels = deployment.get('published_labels', 0)
            label_names = deployment.get('label_names', [])
            
            if published_labels >= 4:
                # Good label deployment (standard baseline is 4+ labels)
                label_list = ', '.join(label_names) if label_names else 'multiple labels'
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"{published_labels} sensitivity labels published ({label_list}), providing comprehensive classification framework for Copilot content protection",
                    recommendation="",
                    link_text="Sensitivity Label Best Practices",
                    link_url="https://learn.microsoft.com/purview/information-protection-deployment",
                    status="Success"
                )
            elif published_labels >= 1:
                # Minimal labels deployed
                label_list = ', '.join(label_names) if label_names else f"{published_labels} label(s)"
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"Only {published_labels} sensitivity label(s) published ({label_list}), providing minimal classification granularity",
                    recommendation=f"Expand sensitivity label taxonomy from {published_labels} to at least 4 labels to properly classify content for Copilot. Recommended baseline: 'Public' (shareable externally), 'General/Internal' (default for internal docs), 'Confidential' (sensitive business data), and 'Highly Confidential' (executive/financial/HR content). Copilot respects these labels when summarizing and sharing content - without granular labels, users can't properly protect sensitive information that Copilot processes. Deploy labels to all users, set 'General' as default, and train teams on when to apply 'Confidential' vs 'Highly Confidential' markings.",
                    link_text="Sensitivity Label Best Practices",
                    link_url="https://learn.microsoft.com/purview/information-protection-deployment",
                    priority="Medium",
                    status="Success"
                )
            else:
                # No labels published
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Label Deployment",
                    observation=f"Information Protection license active but NO sensitivity labels published - zero content classification deployed",
                    recommendation=f"Immediately create and publish sensitivity labels before deploying Copilot at scale. Without labels, Copilot processes all content equally with no protection boundaries. Start with 4 baseline labels: 'Public' (marketing materials, public docs), 'General' (default internal content), 'Confidential' (customer data, contracts, product roadmaps), 'Highly Confidential' (financials, M&A, HR records). Publish labels to all users via Microsoft Purview compliance portal. Train users that Copilot can only share/summarize content according to label restrictions - unlabeled content is treated as 'General' by default. This is CRITICAL before Copilot rollout to prevent data leakage.",
                    link_text="Create Sensitivity Labels",
                    link_url="https://learn.microsoft.com/purview/create-sensitivity-labels",
                    priority="High",
                    status="Success"
                )
        else:
            # Cannot verify label deployment
            error_msg = deployment.get('message', 'Unable to verify label deployment')
            deployment_rec = new_recommendation(
                service="Purview",
                feature=f"{feature_name} - Label Deployment",
                observation=f"Sensitivity label deployment status could not be verified ({error_msg})",
                recommendation="Verify sensitivity label deployment manually in Microsoft Purview compliance portal > Information Protection > Labels. Ensure you have published at least 4 labels: Public, General/Internal, Confidential, and Highly Confidential. Check label policies are assigned to all users. Before Copilot deployment, audit that critical documents are properly labeled to control how Copilot summarizes and shares content across your organization.",
                link_text="Manage Sensitivity Labels",
                link_url="https://learn.microsoft.com/purview/create-sensitivity-labels",
                priority="Medium",
                status="Success"
            )
        
        return [license_rec, deployment_rec]
    
    # Return all recommendations
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    # If license not active or no data, return only license recommendation
