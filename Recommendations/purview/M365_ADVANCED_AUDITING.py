"""
Microsoft 365 Advanced Auditing - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """
    Check audit log configuration and retention settings.
    Returns dict with audit status.
    """
    try:
        # Advanced Auditing configuration is managed through Purview
        # Check if organization has auditing enabled via organization settings
        org_response = await client.organization.get()
        
        if not org_response or not org_response.value:
            return {
                'available': False,
                'has_auditing': False
            }
        
        # Note: Detailed audit policy configuration requires Security & Compliance Center PowerShell
        # Graph API doesn't directly expose audit retention policies
        return {
            'available': True,
            'has_org_config': True,
            'note': 'Detailed audit policies require Purview compliance portal verification'
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        if '401' in error_msg or 'unauthorized' in error_msg:
            return {
                'available': False,
                'error': 'insufficient_permissions',
                'message': 'Organization.Read.All permission required'
            }
        elif '403' in error_msg or 'forbidden' in error_msg:
            return {
                'available': False,
                'error': 'access_denied',
                'message': 'Admin consent required for audit access'
            }
        return {
            'available': False,
            'error': 'unknown',
            'message': f'Unable to check audit status: {str(e)}'
        }

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Advanced Auditing captures detailed Copilot activity logs including prompts,
    data accessed, and AI-generated outputs for compliance and security investigations.
    Returns 2+ recommendations: license status + audit tracking configuration status.
    """
    feature_name = "Microsoft 365 Advanced Auditing"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, logging detailed Copilot interactions and data access patterns",
            recommendation="",
            link_text="Audit Copilot Activity for Compliance",
            link_url="https://learn.microsoft.com/purview/audit-solutions-overview",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing comprehensive audit trails of Copilot usage",
            recommendation=f"Enable {feature_name} to capture extended audit logs (10 years retention) of all M365 Copilot activities - which files were accessed by AI, what prompts users entered, when sensitive data was retrieved by agents, and who modified Copilot settings. Critical for insider risk investigations, compliance audits, and understanding how AI is being used to access organizational data. Required for SOC 2, HIPAA, and financial services compliance.",
            link_text="Audit Copilot Activity for Compliance",
            link_url="https://learn.microsoft.com/purview/audit-solutions-overview",
            priority="High",
            status=status
        )
    
    # Collect deployment recommendations
    deployment_recs = []
    
    # Check PowerShell audit configuration data first (more accurate than Graph API)
    if status == "Success" and purview_client and hasattr(purview_client, 'audit_config'):
        audit_config = purview_client.audit_config
        
        if audit_config.get('available'):
            unified_audit_enabled = audit_config.get('unified_audit_enabled', False)
            admin_audit_enabled = audit_config.get('admin_audit_enabled', False)
            
            if unified_audit_enabled:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration Status",
                    observation=f"Unified Audit Log is ENABLED (Admin Audit: {'Enabled' if admin_audit_enabled else 'Disabled'}) - Copilot events are being logged",
                    recommendation="Verify Advanced Auditing configuration for Copilot: 1) Check audit log retention set to 10 years (not default 90 days) in Purview > Audit > Retention policies, 2) Confirm Copilot event types are captured (CopilotInteraction, PromptSubmitted, SensitiveDataAccessed), 3) Create audit alerts for high-risk patterns (excessive data access, unusual prompts), 4) Export to SIEM for correlation with security events. Review audit logs monthly for compliance reporting.",
                    link_text="Copilot Audit Policies",
                    link_url="https://learn.microsoft.com/purview/audit-log-retention-policies",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration Status",
                    observation="Advanced Auditing license active but Unified Audit Log is DISABLED - NO Copilot events are being logged",
                    recommendation="Enable Unified Audit Log immediately. Run in Exchange Online PowerShell: Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true. Without this, Copilot interactions are NOT logged - no audit trail for compliance, investigations, or insider risk detection. Once enabled, configure: 1) 10-year retention for Copilot events, 2) Alerts for suspicious AI usage patterns, 3) SIEM integration for security monitoring. Audit logging is foundational requirement for Copilot compliance.",
                    link_text="Enable Unified Audit",
                    link_url="https://learn.microsoft.com/purview/audit-log-enable-disable",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    # Return PowerShell-based recommendations if available
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    # Fallback to Graph API check if PowerShell data unavailable
    elif status == "Success" and client:
        deployment = await get_deployment_status(client)
        
        if deployment.get('available') and deployment.get('has_org_config'):
            # Organization configured - provide guidance on Copilot event tracking
            deployment_rec = new_recommendation(
                service="Purview",
                feature=f"{feature_name} - Copilot Event Tracking",
                observation="Advanced Auditing infrastructure available for tracking Copilot events",
                recommendation="Configure Advanced Auditing for comprehensive Copilot event tracking in Microsoft Purview compliance portal: 1) Enable audit logging for Copilot events: CopilotInteraction, PromptSubmitted, AIResponseGenerated, SensitiveDataAccessed, 2) Set retention to 10 years for compliance (vs standard 90 days), 3) Create audit alerts for suspicious patterns: excessive sensitive data access, unusual prompt patterns, after-hours Copilot usage, 4) Export logs to SIEM for correlation with security events. Key events to monitor: which users prompt Copilot about confidential projects, when Copilot accesses HR/financial data, failed permission checks. Review monthly for insider risk and compliance reporting.",
                link_text="Configure Copilot Audit Policies",
                link_url="https://learn.microsoft.com/purview/audit-log-retention-policies",
                priority="Medium",
                status="Success"
            )
        else:
            # Cannot verify audit configuration
            error_msg = deployment.get('message', 'Unable to verify audit configuration')
            deployment_rec = new_recommendation(
                service="Purview",
                feature=f"{feature_name} - Copilot Event Tracking",
                observation=f"Advanced Auditing configuration status could not be verified ({error_msg})",
                recommendation="Manually configure Advanced Auditing for Copilot event tracking in Microsoft Purview compliance portal > Audit > Audit retention policies. Critical configuration: 1) Enable 10-year retention for Copilot event logs (standard is only 90 days), 2) Create audit log policy specifically for Copilot activities: user prompts, AI responses, data access by Copilot, configuration changes, 3) Set up alerts for high-risk events: Copilot accessing highly confidential data, unusual usage patterns, failed permission checks, 4) Integrate with Microsoft Sentinel for advanced threat detection. Regular audit review required for SOC 2, HIPAA, GDPR compliance when deploying Copilot.",
                link_text="Advanced Audit Configuration",
                link_url="https://learn.microsoft.com/purview/audit-log-retention-policies",
                priority="Medium",
                status="Success"
            )
        
        return [license_rec, deployment_rec]
    
    # If license not active or no client, return only license recommendation
    return [license_rec]
