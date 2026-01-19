"""
Azure Information Protection Premium P1 - Purview & Compliance Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Azure Information Protection Premium P1 provides advanced data classification and protection.
    """
    feature_name = "Azure Information Protection Premium P1"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, encrypting sensitive documents accessed by Copilot with rights management",
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
            recommendation=f"Enable {feature_name} to classify, label, and protect sensitive documents and emails with encryption and rights management.",
            link_text="Azure Information Protection",
            link_url="https://learn.microsoft.com/azure/information-protection/",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'irm_config'):
        irm_data = purview_client.irm_config
        
        if irm_data.get('available'):
            azure_rms_enabled = irm_data.get('azure_rms_enabled', False)
            
            if azure_rms_enabled:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Azure Rights Management (Azure RMS) is ENABLED - documents accessed by Copilot can be encrypted with rights management",
                    recommendation="Azure RMS is properly enabled. Ensure rights management policies protect Copilot-accessed content: 1) Configure sensitivity labels to automatically apply encryption when Copilot accesses confidential documents, 2) Set rights policies that persist even when content is summarized or copied via AI, 3) Restrict forwarding/copying of emails containing Copilot-generated sensitive summaries, 4) Apply usage rights (view-only, no-print, no-copy) to documents created through AI assistance. This ensures that even if Copilot makes sensitive data discoverable, rights management controls prevent unauthorized access. Use Get-IRMConfiguration to verify Azure RMS is active and Get-Label to review label-based protection policies.",
                    link_text="Configure Rights Management",
                    link_url="https://learn.microsoft.com/azure/information-protection/configure-policy",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Azure Information Protection Premium P1 license is active but Azure Rights Management (RMS) is DISABLED",
                    recommendation="CRITICAL: Enable Azure Rights Management immediately to activate document encryption capabilities. Without Azure RMS enabled, the AIP Premium P1 license cannot encrypt documents, apply usage rights, or protect sensitive content accessed by Copilot. To enable: Connect to Exchange Online PowerShell and run 'Set-IRMConfiguration -AzureRMSLicensingEnabled $true'. Once enabled, configure sensitivity labels to automatically encrypt: 1) Documents containing financial data that Copilot processes, 2) Emails with customer PII summarized by AI, 3) Confidential files accessed through Copilot searches, 4) AI-generated content containing trade secrets. Azure RMS ensures encrypted content remains protected even when Copilot makes it more discoverable. Use Get-IRMConfiguration to verify activation.",
                    link_text="Enable Azure Rights Management",
                    link_url="https://learn.microsoft.com/azure/information-protection/activate-service",
                    priority="Critical",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
