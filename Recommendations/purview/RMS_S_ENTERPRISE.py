"""
Azure Rights Management - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Azure Rights Management provides persistent document encryption
    that protects sensitive content Copilot accesses and generates.
    """
    feature_name = "Azure Rights Management"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, protecting sensitive content accessed by Copilot with persistent encryption",
            recommendation="",
            link_text="Rights Management for AI Security",
            link_url="https://learn.microsoft.com/azure/information-protection/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, lacking persistent encryption for Copilot-accessed content",
            recommendation=f"Enable {feature_name} to apply persistent encryption and usage rights to documents that Copilot processes. Rights Management ensures that even when Copilot summarizes or extracts from sensitive documents, those protections travel with the content. Prevent unauthorized forwarding of AI-generated summaries, enforce read-only access to Copilot responses containing regulated data, and revoke access to shared content even after distribution. Critical for regulated industries using Copilot with confidential information.",
            link_text="Rights Management for AI Security",
            link_url="https://learn.microsoft.com/azure/information-protection/",
            priority="High",
            status=status
        )
    
    # Check IRM configuration from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'irm_config'):
        irm_config = purview_client.irm_config
        
        if irm_config.get('available'):
            azure_rms_enabled = irm_config.get('azure_rms_enabled', False)
            
            if azure_rms_enabled:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Azure RMS licensing is ENABLED - documents can be protected with persistent encryption",
                    recommendation="Verify Azure RMS protects Copilot scenarios: 1) Test: apply 'Confidential' label to document > ask Copilot to summarize > verify summary inherits protection, 2) Ensure auto-labeling policies protect Copilot outputs containing sensitive patterns (SSN, credit cards), 3) Configure usage rights: prevent AI-generated content marked 'Internal Only' from external sharing, 4) Enable track & revoke for Copilot-created documents. Review protection templates in Azure portal.",
                    link_text="Azure RMS Configuration",
                    link_url="https://learn.microsoft.com/azure/information-protection/configure-policy",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Azure RMS license active but RMS licensing is DISABLED in Exchange/SharePoint",
                    recommendation="Enable Azure RMS in Exchange Online PowerShell: Set-IRMConfiguration -AzureRMSLicensingEnabled $true. Without this, documents cannot be protected with persistent encryption - Copilot-accessed 'Confidential' documents lose protection when shared, AI-generated content with sensitivity labels cannot enforce usage restrictions. Enable RMS to: 1) Protect Copilot summaries of confidential documents, 2) Prevent forwarding of AI-drafted contracts, 3) Track/revoke access to shared Copilot outputs, 4) Enforce read-only on regulated content. Critical for compliance.",
                    link_text="Enable Azure RMS",
                    link_url="https://learn.microsoft.com/azure/information-protection/activate-service",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
