"""
Customer Lockbox - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Customer Lockbox requires explicit approval before Microsoft engineers
    can access your tenant data during Copilot support incidents.
    """
    feature_name = "Customer Lockbox (Enterprise)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, requiring approval for Microsoft access to Copilot-indexed content",
            recommendation="",
            link_text="Control Microsoft Access to AI Content",
            link_url="https://learn.microsoft.com/purview/customer-lockbox-requests",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, allowing uncontrolled Microsoft access during support scenarios",
            recommendation=f"Enable {feature_name} to maintain control when Microsoft Support needs to access your environment to troubleshoot Copilot issues. Ensure that even during technical support incidents, Microsoft engineers cannot view Copilot conversation histories, meeting transcripts, or AI-generated content without explicit approval from your organization. Critical for regulated industries and organizations with strict data access policies that apply even to cloud service providers.",
            link_text="Control Microsoft Access to AI Content",
            link_url="https://learn.microsoft.com/purview/customer-lockbox-requests",
            priority="Low",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'org_config'):
        org_config = purview_client.org_config
        
        if org_config.get('available'):
            lockbox_enabled = org_config.get('customer_lockbox_enabled', False)
            
            if lockbox_enabled:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Customer Lockbox is ENABLED - Microsoft requires your approval to access Copilot data during support",
                    recommendation="Customer Lockbox is properly configured. During Copilot support incidents, you'll receive approval requests before Microsoft engineers can access your data. Ensure: 1) Designated approvers are configured, 2) Approval workflow is tested, 3) Team knows how to respond to lockbox requests, 4) Escalation path defined for urgent support needs. Review requests in Microsoft 365 admin center > Settings > Security & privacy > Customer lockbox.",
                    link_text="Manage Customer Lockbox",
                    link_url="https://learn.microsoft.com/purview/customer-lockbox-requests",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Customer Lockbox license active but feature is DISABLED in tenant settings",
                    recommendation="Enable Customer Lockbox in Microsoft 365 admin center: Settings > Security & privacy > Customer lockbox > Edit > Enable. Once enabled, Microsoft Support must request your approval before accessing Copilot conversation histories, meeting transcripts, or AI-indexed content during troubleshooting. Designated approvers can accept/reject requests. Critical for maintaining data sovereignty and compliance in regulated industries.",
                    link_text="Enable Customer Lockbox",
                    link_url="https://learn.microsoft.com/purview/customer-lockbox-requests#enable-customer-lockbox",
                    priority="Medium",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
