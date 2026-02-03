"""
Copilot Security Posture - Overall Security Assessment
Analyzes security readiness for Microsoft 365 Copilot deployment based on
Defender metrics, exposure score, security recommendations, and threat intelligence.
"""
from Core.new_recommendation import new_recommendation

def get_recommendation(defender_client=None, purview_client=None, defender_insights=None):
    """
    Generate comprehensive Copilot security posture assessment.
    Provides useful analysis even with partial data (degraded mode).
    """
    
    # Determine data availability
    has_defender_api = defender_client and defender_client.available
    has_graph_security = defender_client and defender_client.graph_security_available
    has_purview = purview_client is not None
    
    # Degraded mode - still provide useful analysis with available data
    if not defender_client:
        return new_recommendation(
            service="Defender",
            feature="Copilot Security Posture",
            status="Warning",
            observation="Unable to assess Copilot security posture - Defender client not initialized.",
            recommendation="Ensure Microsoft Defender license is assigned and service principal has required permissions.",
            priority="High",
            link_text="Defender for Endpoint",
            link_url="https://learn.microsoft.com/microsoft-365/security/defender-endpoint/microsoft-defender-endpoint"
        )
    
    # Calculate overall security posture with available data sources
    risk_factors = []
    strengths = []
    critical_gaps = []
    data_limitations = []
    
    # Track what data we're analyzing
    if not has_defender_api:
        data_limitations.append("Defender for Endpoint APIs (device telemetry, vulnerabilities, exposure score)")
    
    # Factor 1: Exposure Score (Defender API - may be unavailable)
    if has_defender_api and defender_client.exposure_summary.get('score', 0) > 0:
        score = defender_client.exposure_summary['score']
        level = defender_client.exposure_summary['level']
        
        if score > 60:
            risk_factors.append(f"High exposure score ({score}/100)")
            critical_gaps.append("Reduce attack surface through patch management and configuration hardening")
        elif score > 30:
            risk_factors.append(f"Medium exposure score ({score}/100)")
        else:
            strengths.append(f"Low exposure score ({score}/100)")
    
    # Factor 2: Critical Security Recommendations
    if defender_client.recommendations_summary.get('critical', 0) > 0:
        critical_count = defender_client.recommendations_summary['critical']
        risk_factors.append(f"{critical_count} critical security recommendations unimplemented")
        critical_gaps.append(f"Address {critical_count} critical security gaps before Copilot deployment")
    
    if defender_client.recommendations_summary.get('copilot_related', 0) > 0:
        copilot_rec_count = defender_client.recommendations_summary['copilot_related']
        risk_factors.append(f"{copilot_rec_count} Copilot-related recommendations pending")
    
    # Factor 3: Compromised Identities (critical for Copilot access control)
    if defender_insights and defender_insights.risky_users_compromised > 0:
        compromised = defender_insights.risky_users_compromised
        risk_factors.append(f"{compromised} confirmed compromised accounts with potential Copilot access")
        critical_gaps.append(f"Immediately revoke access for {compromised} compromised accounts and enforce MFA")
    
    if defender_insights and defender_insights.risky_users_high > 0:
        high_risk = defender_insights.risky_users_high
        risk_factors.append(f"{high_risk} high-risk users")
    
    # Factor 4: Email Threats (Copilot processes email content)
    # Use pre-computed insights if available, otherwise fall back to direct access
    if defender_insights and defender_insights.available:
        if defender_insights.alert_phishing > 10:
            risk_factors.append(f"{defender_insights.alert_phishing} phishing attempts detected (Copilot may process malicious content)")
        if defender_insights.alert_malware > 0:
            risk_factors.append(f"{defender_insights.alert_malware} malware detections in emails")
    elif defender_client and defender_client.email_threat_summary.get('total', 0) > 0:
        threats = defender_client.email_threat_summary
        if threats.get('phishing', 0) > 10:
            risk_factors.append(f"{threats['phishing']} phishing attempts detected (Copilot may process malicious content)")
        if threats.get('malware', 0) > 0:
            risk_factors.append(f"{threats['malware']} malware detections in emails")
    
    # Factor 5: OAuth App Risks (third-party apps accessing Copilot data)
    if defender_insights and defender_insights.oauth_high_risk > 0:
        high_risk_apps = defender_insights.oauth_high_risk
        over_privileged = defender_insights.oauth_over_privileged
        risk_factors.append(f"{high_risk_apps} high-risk third-party apps with excessive permissions")
        
        # Provide specific actionable steps
        oauth_action = f"Review {high_risk_apps} third-party apps: Check Cloud App Security > OAuth apps > Filter by 'High severity'. Revoke apps with: (1) Read/Write access to all SharePoint/OneDrive files, (2) Full mailbox access, (3) Unused apps from unknown publishers, (4) Apps with offline_access requesting refresh tokens"
        if over_privileged > 0:
            oauth_action += f". Prioritize {over_privileged} over-privileged apps first"
        critical_gaps.append(oauth_action)
    elif defender_client and defender_client.oauth_risk_summary.get('high_risk', 0) > 0:
        high_risk_apps = defender_client.oauth_risk_summary['high_risk']
        over_privileged = defender_client.oauth_risk_summary.get('over_privileged', 0)
        risk_factors.append(f"{high_risk_apps} high-risk third-party apps with excessive permissions")
        
        oauth_action = f"Review {high_risk_apps} third-party apps: Check Cloud App Security > OAuth apps > Filter by 'High severity'. Revoke apps with: (1) Read/Write access to all SharePoint/OneDrive files, (2) Full mailbox access, (3) Unused apps from unknown publishers, (4) Apps with offline_access requesting refresh tokens"
        if over_privileged > 0:
            oauth_action += f". Prioritize {over_privileged} over-privileged apps first"
        critical_gaps.append(oauth_action)
    
    # Factor 6: Advanced Hunting - Copilot-specific threats
    if defender_client.hunting_summary.get('suspicious_processes', 0) > 10:
        sus_proc = defender_client.hunting_summary['suspicious_processes']
        risk_factors.append(f"{sus_proc} suspicious Copilot-related process events detected")
    
    if defender_client.hunting_summary.get('phishing_attempts', 0) > 0:
        phish = defender_client.hunting_summary['phishing_attempts']
        risk_factors.append(f"{phish} phishing attempts mentioning Copilot/AI keywords")
        critical_gaps.append("Educate users about AI-themed social engineering attacks")
    
    if defender_client.hunting_summary.get('sensitive_file_access', 0) > 50:
        sensitive_files = defender_client.hunting_summary['sensitive_file_access']
        risk_factors.append(f"{sensitive_files} sensitive files accessed before Copilot use (potential data exposure)")
    
    # Factor 7: Active High-Severity Incidents
    if defender_insights and defender_insights.incident_high_severity > 0:
        high_sev = defender_insights.incident_high_severity
        risk_factors.append(f"{high_sev} high-severity security incidents active")
        critical_gaps.append(f"Resolve {high_sev} high-severity incidents before Copilot deployment")
    elif defender_client and defender_client.incident_summary.get('high_severity', 0) > 0:
        high_sev = defender_client.incident_summary['high_severity']
        risk_factors.append(f"{high_sev} high-severity security incidents active")
        critical_gaps.append(f"Resolve {high_sev} high-severity incidents before Copilot deployment")
    
    # Factor 8: Vulnerable Software (including Copilot apps)
    if defender_client.software_summary.get('vulnerable_apps', 0) > 10:
        vuln_apps = defender_client.software_summary['vulnerable_apps']
        risk_factors.append(f"{vuln_apps} applications with known vulnerabilities")
    
    # Factor 9: Device Risks
    if defender_client.device_summary.get('high_risk', 0) > 0:
        high_risk_devices = defender_client.device_summary['high_risk']
        total_devices = defender_client.device_summary.get('total', 0)
        if total_devices > 0:
            risk_pct = (high_risk_devices / total_devices) * 100
            if risk_pct > 10:  # More than 10% high-risk devices
                risk_factors.append(f"{high_risk_devices} high-risk devices ({risk_pct:.0f}% of fleet)")
                critical_gaps.append("Implement conditional access to block high-risk devices from Copilot")
    
    # Factor 10: Purview Data Governance (if available)
    if purview_client and purview_client.dlp_policies.get('available'):
        dlp_enabled = purview_client.dlp_policies.get('enabled_policies', 0)
        dlp_total = purview_client.dlp_policies.get('total_policies', 0)
        
        if dlp_total == 0:
            risk_factors.append("No DLP policies deployed (Copilot can share sensitive data without protection)")
            critical_gaps.append("Deploy DLP policies to prevent Copilot from exposing sensitive information")
        elif dlp_enabled < dlp_total:
            risk_factors.append(f"{dlp_total - dlp_enabled} DLP policies not enabled")
    
    if purview_client and purview_client.sensitivity_labels.get('available'):
        labels_count = purview_client.sensitivity_labels.get('total_labels', 0)
        if labels_count == 0:
            risk_factors.append("No sensitivity labels deployed (data classification missing)")
            critical_gaps.append("Deploy sensitivity labels to control what data Copilot can access")
    
    # Calculate overall posture
    total_risk_factors = len(risk_factors)
    total_strengths = len(strengths)
    total_critical_gaps = len(critical_gaps)
    
    if total_critical_gaps > 0:
        status = "Critical"
        posture = "NOT READY"
        importance = "High"  # Map Critical to High priority
    elif total_risk_factors > 5:
        status = "Warning"
        posture = "AT RISK"
        importance = "High"
    elif total_risk_factors > 2:
        status = "Attention Required"
        posture = "NEEDS IMPROVEMENT"
        importance = "Medium"
    else:
        status = "Success"
        posture = "READY"
        importance = "Low"
    
    # Build observation
    observation_parts = [f"Copilot Security Posture: **{posture}**"]
    
    if total_critical_gaps > 0:
        observation_parts.append(f"\n\n**{total_critical_gaps} Critical Gaps:**")
        for gap in critical_gaps[:5]:  # Top 5 critical gaps
            observation_parts.append(f"  - {gap}")
    
    if total_risk_factors > 0:
        observation_parts.append(f"\n\n**{total_risk_factors} Risk Factors Detected:**")
        for risk in risk_factors[:10]:  # Top 10 risks
            observation_parts.append(f"  - {risk}")
    
    if total_strengths > 0:
        observation_parts.append(f"\n\n**{total_strengths} Strengths:**")
        for strength in strengths:
            observation_parts.append(f"  - {strength}")
    
    # Note data limitations for partial analysis
    if data_limitations:
        observation_parts.append(f"\n\n**⚠️ Limited Analysis** - Missing data from:")
        for limitation in data_limitations:
            observation_parts.append(f"  - {limitation}")
        observation_parts.append("\nFor complete assessment, onboard devices to Defender for Endpoint.")
    
    observation = "\n".join(observation_parts)
    
    # Build recommendation (importance already set above)
    if total_critical_gaps > 0:
        recommendation = (
            f"Address {total_critical_gaps} critical security gaps before broad Copilot deployment:\n\n"
            "1. Identity: Use Entra ID Protection > Risky users > Confirm compromised > Reset password + Revoke sessions\n"
            "2. Incidents: Defender XDR > Incidents > Filter High severity > Investigate and remediate\n"
            "3. OAuth Apps: Cloud App Security > OAuth apps > Review high-risk > Revoke unnecessary permissions\n"
            "4. DLP: Purview > Data Loss Prevention > Create policy for Copilot (SharePoint, OneDrive, Teams, Exchange)\n\n"
            "Consider phased rollout to pilot group while remediating critical gaps."
        )
    elif total_risk_factors > 5:
        recommendation = (
            f"Mitigate {total_risk_factors} security risks before full-scale rollout:\n\n"
            "- Enable Conditional Access requiring compliant devices and MFA for Copilot\n"
            "- Deploy baseline DLP policies for financial data, PII, and source code\n"
            "- Implement continuous monitoring using Defender XDR workbook for Copilot\n"
            "- Conduct security awareness training on AI-themed phishing\n\n"
            "Safe to pilot with IT/security team while improving overall posture."
        )
    elif total_risk_factors > 2:
        recommendation = (
            f"Address {total_risk_factors} moderate risks. Copilot deployment can proceed with enhanced monitoring:\n\n"
            "- Enable audit logging for all Copilot activities\n"
            "- Configure alerts for suspicious Copilot usage patterns\n"
            "- Review security metrics weekly during initial rollout\n"
            "- Deploy with existing security controls and iterate based on findings."
        )
    else:
        recommendation = (
            "Security posture is strong for Copilot deployment. Continue best practices:\n\n"
            "- Review Defender recommendations monthly\n"
            "- Monitor Copilot-specific threat intelligence\n"
            "- Update security policies as Copilot features expand\n"
            "- Maintain regular security awareness training."
        )
    
    return new_recommendation(
        service="Defender",
        feature="Copilot Security Posture",
        status=status,
        observation=observation,
        recommendation=recommendation,
        priority=importance,
        link_text="Copilot Security",
        link_url="https://learn.microsoft.com/microsoft-365-copilot/microsoft-365-copilot-security"
    )
