"""
Microsoft 365 Audit Platform - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    M365 Audit Platform provides comprehensive logging of user
    activities including Copilot usage for compliance and investigation.
    """
    feature_name = "Microsoft 365 Audit Platform"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, logging Copilot activities for compliance and security",
            recommendation="",
            link_text="Audit Copilot Usage",
            link_url="https://learn.microsoft.com/purview/audit-solutions-overview/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, lacking comprehensive audit logging for AI usage",
            recommendation=f"Enable {feature_name} to capture detailed logs of Copilot usage including prompts submitted, content accessed, and responses generated. Audit logs provide forensic evidence for investigating potential misuse, demonstrate compliance with data handling policies, and measure adoption patterns. Track which users leverage Copilot, what content they access through AI, and identify unusual usage that may indicate security concerns. Critical for regulated industries that must audit all access to sensitive information, including AI-mediated access.",
            link_text="Audit Copilot Usage",
            link_url="https://learn.microsoft.com/purview/audit-solutions-overview/",
            priority="High",
            status=status
        )
    
    # Check audit configuration from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'audit_config'):
        audit_config = purview_client.audit_config
        
        if audit_config.get('available'):
            unified_enabled = audit_config.get('unified_audit_enabled', False)
            admin_enabled = audit_config.get('admin_audit_enabled', False)
            
            if unified_enabled:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Audit Status",
                    observation=f"Audit logging ENABLED (Unified: Yes, Admin: {'Yes' if admin_enabled else 'No'}) - Copilot activities are logged",
                    recommendation="Verify Copilot event logging: 1) Search audit log in Purview for 'Copilot' activities, 2) Confirm events captured: file access by Copilot, prompt submissions, AI responses with sensitive data, 3) Set retention to match compliance requirements (default 90 days, up to 10 years with Advanced Auditing), 4) Create alerts: unusual Copilot usage volumes, access to highly confidential content, after-hours AI activity. Export logs to SIEM for security correlation.",
                    link_text="Search Copilot Audit Logs",
                    link_url="https://learn.microsoft.com/purview/audit-log-search",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Audit Status",
                    observation="Audit Platform license active but Unified Audit is DISABLED - NO Copilot events logged",
                    recommendation="Enable audit logging IMMEDIATELY. Run in Exchange Online PowerShell: Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true. Without auditing: 1) No record of Copilot accessing sensitive data (compliance violation), 2) Cannot investigate security incidents involving AI, 3) No visibility into insider risk via Copilot, 4) Fail regulatory audits (SOC 2, HIPAA, GDPR require audit trails). Enable now before Copilot adoption scales.",
                    link_text="Enable Audit Logging",
                    link_url="https://learn.microsoft.com/purview/audit-log-enable-disable",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
