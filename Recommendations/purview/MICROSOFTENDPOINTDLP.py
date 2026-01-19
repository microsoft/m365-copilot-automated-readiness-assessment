"""
Microsoft Endpoint DLP - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Endpoint DLP prevents sensitive data from being copied from Copilot responses
    to unauthorized locations, securing AI-generated content at the device level.
    """
    feature_name = "Microsoft Endpoint DLP"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, protecting against data exfiltration through Copilot outputs",
            recommendation="",
            link_text="Endpoint DLP for Copilot Security",
            link_url="https://learn.microsoft.com/purview/endpoint-dlp-learn-about",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, leaving AI-generated sensitive data unprotected on endpoints",
            recommendation=f"Enable {feature_name} to prevent users from copying sensitive information from Copilot responses to personal email, USB drives, or unapproved cloud storage. When Copilot retrieves confidential data (financial reports, customer PII, trade secrets) and presents it to users, Endpoint DLP ensures that information cannot leave the corporate environment through copy/paste, screenshots, or file transfers. This addresses the unique risk that AI assistants make it very easy to aggregate and exfiltrate large amounts of sensitive data quickly.",
            link_text="Endpoint DLP for Copilot Security",
            link_url="https://learn.microsoft.com/purview/endpoint-dlp-learn-about",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'dlp_policies'):
        dlp_data = purview_client.dlp_policies
        
        if dlp_data.get('available'):
            total_policies = dlp_data.get('total_policies', 0)
            endpoint_policies = dlp_data.get('endpoint_policies', 0)
            
            if total_policies > 0 and endpoint_policies > 0:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Active Policies",
                    observation=f"Endpoint DLP has {endpoint_policies} active endpoint-scoped policy/policies (of {total_policies} total DLP policies)",
                    recommendation=f"You have {endpoint_policies} Endpoint DLP policy/policies protecting devices from Copilot-related data exfiltration. Ensure these policies: 1) Block copying sensitive Copilot responses to personal email/USB drives/unauthorized cloud storage, 2) Prevent screenshots of confidential AI-generated content, 3) Restrict printing documents that Copilot creates from sensitive sources, 4) Monitor file transfers when users export Copilot summaries containing PII/financial data. Review policy scopes to cover all devices where users access Copilot (Windows endpoints, macOS if deployed). Verify rules detect content patterns common in AI outputs (aggregated data, multi-source summaries, formatted reports). Use Get-DlpCompliancePolicy to audit configurations.",
                    link_text="Manage Endpoint DLP Policies",
                    link_url="https://learn.microsoft.com/purview/endpoint-dlp-using",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            elif total_policies > 0:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation=f"DLP policies exist ({total_policies} total) but NONE are configured for endpoint protection",
                    recommendation=f"You have {total_policies} DLP policy/policies but none target endpoints. Create endpoint-scoped policies to prevent Copilot data exfiltration: 1) Block users from copying sensitive Copilot responses to USB drives, personal email, or unauthorized cloud storage, 2) Prevent exfiltration when Copilot retrieves customer PII, financial data, or intellectual property, 3) Monitor file transfers of AI-generated documents to personal devices, 4) Restrict printing/screenshots of confidential Copilot outputs. Configure in Purview compliance portal > Data loss prevention > Policies > Create policy > Select 'Devices' location. Apply policies to all Windows endpoints where Copilot is used. Use Get-DlpCompliancePolicy to verify endpoint coverage.",
                    link_text="Create Endpoint DLP Policies",
                    link_url="https://learn.microsoft.com/purview/endpoint-dlp-getting-started",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Endpoint DLP license is active but NO DLP policies are configured",
                    recommendation="Create Endpoint DLP policies BEFORE users start exfiltrating Copilot-generated sensitive data. Deploy policies to: 1) Block copying confidential Copilot responses to personal email, USB drives, or unauthorized cloud storage, 2) Prevent users from taking screenshots of sensitive AI outputs, 3) Restrict printing financial reports or customer data that Copilot aggregates, 4) Monitor file transfers when users export Copilot summaries to personal devices. Start with high-value content types (SSN, credit card numbers, financial data, customer PII) and expand to trade secrets and intellectual property. Configure in Purview compliance portal > Data loss prevention > Policies. Use Get-DlpCompliancePolicy to verify deployment.",
                    link_text="Deploy Endpoint DLP",
                    link_url="https://learn.microsoft.com/purview/endpoint-dlp-getting-started",
                    priority="Critical",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
