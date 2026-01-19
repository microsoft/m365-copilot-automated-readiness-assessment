"""
Copilot Data Governance - Compliance & Protection Assessment
Evaluates data governance readiness for Copilot using Purview policies,
DLP rules, sensitivity labels, and data access controls.
"""
from new_recommendation import new_recommendation

def get_recommendation(purview_client=None, defender_client=None, defender_insights=None):
    """
    Generate Copilot data governance assessment from Purview and Defender data.
    Critical for ensuring Copilot doesn't expose or leak sensitive information.
    """
    
    if not purview_client:
        return new_recommendation(
            service="Defender",
            feature="Copilot Data Governance",
            status="Warning",
            observation="Unable to assess Copilot data governance - Purview data not available. Run tool with: .\\collect_purview_data.ps1",
            recommendation="Enable Microsoft Purview to assess and enforce data governance for Copilot. Includes DLP, sensitivity labels, retention policies, and information barriers.",
            priority="High",
            link_text="Purview for AI",
            link_url="https://learn.microsoft.com/purview/ai-microsoft-purview"
        )
    
    gaps = []
    strengths = []
    recommendations = []
    critical_gaps = []
    
    # Assessment 1: DLP Policies (prevent data leakage through Copilot)
    if purview_client.dlp_policies.get('available'):
        dlp_total = purview_client.dlp_policies.get('total_policies', 0)
        dlp_enabled = purview_client.dlp_policies.get('enabled_policies', 0)
        
        if dlp_total == 0:
            gaps.append("**No DLP policies deployed** - Copilot can share sensitive data without protection")
            critical_gaps.append("Deploy DLP policies immediately")
            recommendations.append(
                "Deploy DLP policies for Copilot: Create policies to detect and block sharing of: "
                "credit card numbers, social security numbers, financial data, health records, source code. "
                "Apply to: Teams, SharePoint, OneDrive, Exchange (all Copilot data sources). "
                "Use 'Block' action for highly sensitive content, 'Notify' for moderate risk."
            )
        elif dlp_enabled < dlp_total:
            gaps.append(f"{dlp_total - dlp_enabled} DLP policies configured but not enabled")
            recommendations.append(f"Enable {dlp_total - dlp_enabled} dormant DLP policies to protect Copilot data")
        else:
            strengths.append(f"{dlp_enabled} active DLP policies protecting Copilot data sources")
    else:
        gaps.append("DLP policy data unavailable - run .\\collect_purview_data.ps1 to enable Purview data collection")
        critical_gaps.append("Enable Purview PowerShell module to assess DLP coverage. Without DLP visibility, cannot verify Copilot data leakage protection. Run: Install-Module -Name ExchangeOnlineManagement; Connect-IPPSSession")
    
    # Assessment 2: Sensitivity Labels (data classification for Copilot access control)
    if purview_client.sensitivity_labels.get('available'):
        labels_count = purview_client.sensitivity_labels.get('total_labels', 0)
        
        if labels_count == 0:
            gaps.append("**No sensitivity labels deployed** - Cannot control which data Copilot can access")
            critical_gaps.append("Deploy sensitivity labels immediately")
            recommendations.append(
                "Deploy sensitivity labels: Create label hierarchy: Public, Internal, Confidential, Highly Confidential. "
                "Configure Copilot to respect labels (E5 feature). "
                "Auto-apply labels to files containing PII, financial data, or legal content. "
                "Set policies: 'Highly Confidential' files not accessible via Copilot without explicit permissions."
            )
        elif labels_count < 3:
            gaps.append(f"Only {labels_count} sensitivity labels - insufficient granularity for Copilot access control")
            recommendations.append("Deploy comprehensive label taxonomy with at least 4 levels: Public, Internal, Confidential, Highly Confidential")
        else:
            strengths.append(f"{labels_count} sensitivity labels deployed for data classification")
            
            # Check if label policies are configured
            if purview_client.label_policies.get('available'):
                policy_count = purview_client.label_policies.get('total_policies', 0)
                if policy_count == 0:
                    gaps.append("Sensitivity labels exist but no policies deployed - labels not enforced")
                    recommendations.append("Create label policies to auto-apply and enforce sensitivity labels")
                else:
                    strengths.append(f"{policy_count} label policies enforcing classification")
    else:
        gaps.append("Sensitivity label data unavailable - Purview module not loaded")
        critical_gaps.append("Enable Purview data collection to assess label coverage. Run: .\\collect_purview_data.ps1 or manually: Connect-IPPSSession; Get-Label. Labels are critical to control which classified files Copilot can access (E5 Copilot respects Highly Confidential label restrictions)")
    
    # Assessment 3: Information Barriers (prevent Copilot from bridging separated data)
    if purview_client.information_barriers.get('available'):
        ib_count = purview_client.information_barriers.get('total_policies', 0)
        
        if ib_count > 0:
            strengths.append(f"{ib_count} information barrier policies preventing cross-departmental data access via Copilot")
        else:
            # Information barriers are not required for all orgs, only those with compliance requirements
            gaps.append("No information barriers configured - Copilot can access data across all departments")
            recommendations.append(
                "Consider information barriers if your organization requires data separation "
                "(e.g., financial services, legal, HR). This prevents Copilot from using data from "
                "restricted departments in responses to unauthorized users."
            )
    
    # Assessment 4: Insider Risk Policies (detect malicious Copilot usage)
    if purview_client.insider_risk.get('available'):
        insider_risk_count = purview_client.insider_risk.get('total_policies', 0)
        
        if insider_risk_count > 0:
            strengths.append(f"{insider_risk_count} insider risk policies monitoring for data exfiltration via Copilot")
        else:
            gaps.append("No insider risk management policies - cannot detect malicious Copilot usage")
            recommendations.append(
                "Deploy Insider Risk Management policies to detect: "
                "Excessive Copilot queries for sensitive data, copying responses to external email, "
                "unusual access patterns (e.g., accessing customer data outside normal role). "
                "Create policies for: Data theft, Data leaks, Offensive or inappropriate usage."
            )
    
    # Assessment 5: Communication Compliance (detect policy violations in Copilot chats)
    if purview_client.comm_compliance.get('available'):
        comm_comp_count = purview_client.comm_compliance.get('total_policies', 0)
        
        if comm_comp_count > 0:
            strengths.append(f"{comm_comp_count} communication compliance policies scanning Copilot conversations")
        else:
            gaps.append("No communication compliance policies - cannot detect inappropriate Copilot usage")
            recommendations.append(
                "Configure communication compliance to monitor Copilot chats for: "
                "Offensive language, harassment, regulatory violations (e.g., discussing insider trading), "
                "sensitive data sharing, or attempts to bypass security controls."
            )
    
    # Assessment 6: Retention Policies (preserve Copilot audit trail)
    if purview_client.retention_labels.get('available'):
        retention_count = purview_client.retention_labels.get('total_labels', 0)
        
        if retention_count > 0:
            strengths.append(f"{retention_count} retention labels preserving Copilot data for compliance")
        else:
            gaps.append("No retention policies - Copilot interactions may be deleted before audit/investigation")
            recommendations.append(
                "Deploy retention policies for Copilot data: "
                "Retain Teams/Outlook Copilot interactions for minimum 7 years (adjust per industry regulation). "
                "Preserve Copilot audit logs for security investigations. "
                "Consider litigation hold for users under investigation."
            )
    
    # Assessment 7: Audit Logging (track Copilot usage)
    if purview_client.audit_config.get('available'):
        audit_enabled = purview_client.audit_config.get('unified_audit_enabled', False)
        
        if audit_enabled:
            strengths.append("Unified audit logging enabled - Copilot activities are tracked")
        else:
            gaps.append("**Unified audit logging disabled** - No visibility into Copilot usage")
            critical_gaps.append("Enable unified audit logging immediately")
            recommendations.append(
                "Enable unified audit logging: "
                "This captures Copilot query logs, file access via Copilot, plugin usage, and data operations. "
                "Critical for security investigations, compliance audits, and user behavior analytics. "
                "Run: Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true"
            )
    
    # Assessment 8: Defender data - DLP incident correlation
    if defender_client and defender_client.available:
        # Check for DLP-related security alerts
        if defender_client.alert_summary.get('by_category', {}).get('DataLossPrevention', 0) > 0:
            dlp_alerts = defender_client.alert_summary['by_category']['DataLossPrevention']
            gaps.append(f"{dlp_alerts} DLP violations detected - users attempting to share sensitive data through Copilot")
            recommendations.append("Investigate DLP alerts: Review which users triggered DLP policies via Copilot and strengthen controls")
    
    # Calculate overall data governance posture
    total_gaps = len(gaps)
    total_critical_gaps = len(critical_gaps)
    total_strengths = len(strengths)
    
    if total_critical_gaps > 0:
        status = "Critical"
        posture = "UNPROTECTED"
        importance = "High"  # Map Critical to High priority
    elif total_gaps > 5:
        status = "Warning"
        posture = "AT RISK"
        importance = "High"
    elif total_gaps > 2:
        status = "Attention Required"
        posture = "NEEDS IMPROVEMENT"
        importance = "Medium"
    else:
        status = "Success"
        posture = "PROTECTED"
        importance = "Low"
    
    # Build observation
    observation_parts = [f"Copilot Data Governance Posture: **{posture}**"]
    
    if total_critical_gaps > 0:
        observation_parts.append(f"\n\n**{total_critical_gaps} Critical Data Protection Gaps:**")
        for gap in critical_gaps:
            observation_parts.append(f"  - {gap}")
    
    if total_gaps > 0:
        observation_parts.append(f"\n\n**{total_gaps} Governance Gaps:**")
        for gap in gaps[:8]:  # Top 8 gaps
            observation_parts.append(f"  - {gap}")
    
    if total_strengths > 0:
        observation_parts.append(f"\n\n**{total_strengths} Data Protection Controls Active:**")
        for strength in strengths:
            observation_parts.append(f"  - {strength}")
    
    observation = "\n".join(observation_parts)
    
    # Build recommendation (importance already set above)
    if total_critical_gaps > 0:
        recommendation_text = (
            f"{total_critical_gaps} critical data protection gaps require attention:\n\n"
            "IMMEDIATE ACTIONS:\n"
            "1. Deploy baseline DLP policy: Purview > Data Loss Prevention > Create policy > Name: 'Copilot - Sensitive Data Protection' > Locations: SharePoint, OneDrive, Teams, Exchange > Content: Credit cards, SSN, HIPAA, Financial > Action: Block sharing + Notify user\n\n"
            "2. Create sensitivity labels: Purview > Information Protection > Labels > New label > Tiers: Public, Internal, Confidential, Highly Confidential > Configure encryption and access controls\n\n"
            "3. Enable audit logging: Purview > Audit > Turn on auditing (captures all Copilot queries)\n\n"
            "4. Apply auto-labeling: Create policy to automatically label files with PII as 'Confidential'\n\n"
            "Copilot can be piloted with IT/Finance teams while DLP/labels roll out to production. Consider read-only Copilot mode until data protection matures." +
            ("\n\nADDITIONAL STEPS:\n" + "\n".join(recommendations[:2]) if recommendations else "")
        )
    elif total_gaps > 5:
        recommendation_text = (
            f"Strengthen data governance before full rollout ({total_gaps} gaps identified):\n\n"
            "RECOMMENDED ACTIONS:\n"
            "- Expand DLP coverage to all Copilot data sources (currently gaps exist)\n"
            "- Deploy auto-apply label policies for common data types\n"
            "- Enable insider risk management to detect data exfiltration via Copilot\n"
            "- Configure communication compliance for Copilot chat monitoring\n\n"
            "Safe to deploy Copilot to controlled pilot groups. Monitor DLP incidents weekly and expand labels iteratively." +
            ("\n\nDETAILED GUIDANCE:\n" + "\n\n".join(recommendations[:3]) if recommendations else "")
        )
    elif total_gaps > 2:
        recommendation_text = (
            f"Data governance is functional with {total_gaps} improvement areas. Copilot deployment can proceed:\n\n"
            "- Continue enhancing label taxonomy and auto-labeling rules\n"
            "- Monitor DLP policy effectiveness and tune false positives\n"
            "- Review Copilot audit logs monthly for unusual access patterns\n"
            "- Educate users on appropriate Copilot usage with sensitive data" +
            ("\n\n" + "\n\n".join(recommendations) if recommendations else "")
        )
    else:
        recommendation_text = (
            f"Data governance is robust ({total_strengths} active controls). Continue maturity improvements:\n\n"
            "- Review DLP incidents monthly and refine policies\n"
            "- Update label policies as new Copilot features release\n"
            "- Conduct quarterly governance reviews with compliance team\n"
            "- Stay current with Purview AI governance capabilities."
        )
    
    return new_recommendation(
        service="Defender",
        feature="Copilot Data Governance",
        status=status,
        observation=observation,
        recommendation=recommendation_text,
        priority=importance,
        link_text="Purview for Copilot",
        link_url="https://learn.microsoft.com/purview/ai-microsoft-purview-copilot"
    )
