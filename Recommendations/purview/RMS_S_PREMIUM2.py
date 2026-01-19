"""
Azure Information Protection Premium P2 - Purview & Compliance Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Azure Information Protection Premium P2 provides advanced data classification, protection, and discovery.
    """
    feature_name = "Azure Information Protection Premium P2"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, automatically classifying and protecting sensitive data that Copilot processes",
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
            recommendation=f"Enable {feature_name} to automatically classify and protect sensitive data with machine learning and advanced analytics.",
            link_text="Azure Information Protection P2",
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
                    observation="Azure Rights Management (Azure RMS) is ENABLED - advanced automatic classification and protection is available for Copilot-accessed content",
                    recommendation="Azure RMS is properly enabled, unlocking Premium P2's advanced capabilities. Configure automatic classification and protection for Copilot scenarios: 1) Deploy trainable classifiers to detect when Copilot outputs contain industry-specific sensitive data (medical records, legal briefs, financial models), 2) Use automatic labeling with encryption for AI-generated content containing PII or confidential business information, 3) Apply usage rights (view-only, no-forward) to documents that Copilot creates from multiple sensitive sources, 4) Enable content scanning to discover existing unprotected files that Copilot might access. Premium P2's machine learning can identify sensitive content patterns in Copilot outputs that rule-based systems miss. Use Get-IRMConfiguration to verify Azure RMS status and configure auto-labeling policies in Purview compliance portal.",
                    link_text="Configure Advanced Protection",
                    link_url="https://learn.microsoft.com/purview/apply-sensitivity-label-automatically",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Azure Information Protection Premium P2 license is active but Azure Rights Management (RMS) is DISABLED - advanced features are unavailable",
                    recommendation="CRITICAL: Enable Azure Rights Management immediately to unlock Premium P2's advanced automatic classification and machine learning capabilities. Without Azure RMS, you cannot use trainable classifiers, automatic labeling with encryption, or advanced analytics - effectively wasting the Premium P2 investment. To enable: Connect to Exchange Online PowerShell and run 'Set-IRMConfiguration -AzureRMSLicensingEnabled $true'. Once enabled, Premium P2 provides: 1) Trainable classifiers that detect sensitive content in Copilot outputs using machine learning, 2) Automatic encryption of AI-generated documents containing confidential patterns, 3) Content scanning to discover unprotected files Copilot might access, 4) Advanced analytics showing how Copilot interacts with protected content. Enable Azure RMS NOW to protect against data leaks through AI-assisted content discovery. Use Get-IRMConfiguration to verify activation.",
                    link_text="Enable Azure Rights Management",
                    link_url="https://learn.microsoft.com/azure/information-protection/activate-service",
                    priority="Critical",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
