"""
Copilot Threat Intelligence - Advanced Security Insights
Analyzes Advanced Hunting results, threat patterns, and suspicious activities
specifically related to Copilot/AI usage in the tenant.
"""
from new_recommendation import new_recommendation

def get_recommendation(defender_client=None, defender_insights=None):
    """
    Generate Copilot-specific threat intelligence from available security data.
    Provides partial analysis even without Advanced Hunting (degraded mode using Graph Security).
    """
    
    if not defender_client:
        return new_recommendation(
            service="Defender",
            feature="Copilot Threat Intelligence",
            status="Warning",
            observation="Unable to generate threat intelligence - Defender client not initialized.",
            recommendation="Ensure Microsoft Defender license is assigned and service principal has required permissions.",
            priority="High",
            link_text="Microsoft Defender",
            link_url="https://learn.microsoft.com/microsoft-365/security/defender/"
        )
    
    threats_detected = []
    recommendations = []
    threat_count = 0
    data_sources_used = []
    data_sources_missing = []
    
    # Check data availability
    has_defender_api = defender_client.available
    has_graph_security = defender_client.graph_security_available
    
    if not has_defender_api:
        data_sources_missing.append("Advanced Hunting queries (requires devices onboarded)")
        data_sources_missing.append("Device telemetry (process, network, file events)")
    
    # Still analyze available Graph Security data even without Defender API
    if has_graph_security:
        data_sources_used.append("Graph Security API (incidents, alerts, risky users)")
    
    # Analyze 1: Suspicious Process Activity (Defender API - may be unavailable)
    if has_defender_api and defender_client.hunting_summary.get('suspicious_processes', 0) > 0:
        sus_proc = defender_client.hunting_summary['suspicious_processes']
        threat_count += 1
        
        # Get details if available
        if defender_client.copilot_process_events.get('count', 0) > 0:
            results = defender_client.copilot_process_events.get('results', [])
            top_device = results[0].get('DeviceName', 'Unknown') if results else 'Unknown'
            top_account = results[0].get('AccountName', 'Unknown') if results else 'Unknown'
            
            threats_detected.append(
                f"**Suspicious Process Activity:** {sus_proc} process events involving Copilot keywords detected. "
                f"Top affected: Device '{top_device}', User '{top_account}'. "
                "This may indicate automated prompt injection attempts or malicious use of AI features."
            )
            recommendations.append(
                "Investigate suspicious process activity: Review Advanced Hunting logs for "
                "DeviceProcessEvents involving Copilot. Look for script-based automation, "
                "unusual command-line arguments, or processes spawned by unexpected parents."
            )
    
    # Analyze 2: Unusual Network Activity (data exfiltration via Copilot)
    if defender_client.hunting_summary.get('unusual_network_activity', 0) > 100:  # Threshold: >100 unusual connections
        network_events = defender_client.hunting_summary['unusual_network_activity']
        threat_count += 1
        
        # Get details
        if defender_client.copilot_network_events.get('count', 0) > 0:
            results = defender_client.copilot_network_events.get('results', [])
            top_result = results[0] if results else {}
            data_sent_mb = top_result.get('DataSentMB', 0)
            urls = top_result.get('RemoteURLs', [])
            
            threats_detected.append(
                f"**Unusual Network Activity:** {network_events} high-volume network connections to Copilot/AI services detected. "
                f"Top transfer: {data_sent_mb:.1f} MB sent to {len(urls)} unique URLs. "
                "This may indicate data exfiltration through AI conversation interfaces or plugin abuse."
            )
            recommendations.append(
                "Monitor network egress: Review DeviceNetworkEvents for large data transfers to "
                "copilot/AI domains. Implement DLP policies to detect sensitive data in Copilot prompts. "
                "Consider network policies to restrict Copilot plugin access to approved services only."
            )
    
    # Analyze 3: Sensitive File Access (risk of exposing confidential data to Copilot)
    if defender_client.hunting_summary.get('sensitive_file_access', 0) > 50:
        file_access = defender_client.hunting_summary['sensitive_file_access']
        threat_count += 1
        
        if defender_client.copilot_file_access_events.get('count', 0) > 0:
            results = defender_client.copilot_file_access_events.get('results', [])
            top_result = results[0] if results else {}
            file_count = top_result.get('UniqueSensitiveFiles', 0)
            account = top_result.get('AccountName', 'Unknown')
            
            threats_detected.append(
                f"**Sensitive File Access:** {file_access} sensitive files accessed before/during Copilot usage. "
                f"Top user '{account}' accessed {file_count} unique sensitive files. "
                "Risk: Copilot may inadvertently expose confidential content through chat summaries or recommendations."
            )
            recommendations.append(
                "Implement data protection: Deploy sensitivity labels on confidential files. "
                "Configure Copilot to respect sensitivity labels (requires Purview). "
                "Audit file access patterns and correlate with Copilot usage logs. "
                "Consider conditional access policies for users handling highly sensitive data."
            )
    
    # Analyze 4: Phishing Attacks Mentioning Copilot/AI (social engineering)
    if defender_client.hunting_summary.get('phishing_attempts', 0) > 0:
        phishing = defender_client.hunting_summary['phishing_attempts']
        threat_count += 1
        
        if defender_client.copilot_email_threats.get('count', 0) > 0:
            results = defender_client.copilot_email_threats.get('results', [])
            top_result = results[0] if results else {}
            total_threats = top_result.get('TotalThreats', 0)
            senders = top_result.get('UniqueSenders', 0)
            
            threats_detected.append(
                f"**AI-Themed Phishing:** {phishing} phishing attempts detected mentioning 'Copilot', 'AI', or 'ChatGPT' in subject lines. "
                f"From {senders} unique malicious senders, total {total_threats} threat emails. "
                "Attackers are exploiting AI hype to trick users into credential theft or malware installation."
            )
            recommendations.append(
                "User awareness training: Educate users about AI-themed social engineering attacks. "
                "Common tactics: Fake 'Copilot license expiring' emails, malicious 'Copilot plugin' downloads, "
                "phishing sites impersonating Microsoft Copilot login pages. "
                "Enable Safe Links and Safe Attachments in Defender for Office 365."
            )
    
    # Analyze 5: Compromised Accounts Using Copilot (identity-based threats)
    if defender_client.risky_users_summary.get('confirmed_compromised', 0) > 0:
        compromised = defender_client.risky_users_summary['confirmed_compromised']
        threat_count += 1
        
        threats_detected.append(
            f"**Compromised Accounts:** {compromised} confirmed compromised accounts have potential Copilot access. "
            "Risk: Attackers can use Copilot to discover sensitive information, generate phishing content, "
            "or exfiltrate data through natural language queries without triggering traditional DLP."
        )
        recommendations.append(
            "Immediate remediation: Revoke sessions for compromised accounts. "
            "Force password reset and MFA enrollment. "
            "Review Copilot audit logs for unusual queries (e.g., 'show me all financial data', 'export customer list'). "
            "Implement Conditional Access policy: Block Copilot access from risky sign-ins or unmanaged devices."
        )
    
    # Analyze 6: High-Risk OAuth Apps (third-party plugin abuse)
    if defender_client.oauth_risk_summary.get('high_risk', 0) > 0:
        high_risk_apps = defender_client.oauth_risk_summary['high_risk']
        over_privileged = defender_client.oauth_risk_summary.get('over_privileged', 0)
        threat_count += 1
        
        threats_detected.append(
            f"**Third-Party App Risks:** {high_risk_apps} high-risk OAuth apps with excessive permissions detected. "
            f"{over_privileged} apps are over-privileged (>10 scopes). "
            "Risk: Malicious or compromised plugins can exfiltrate data accessed by Copilot or inject malicious prompts."
        )
        recommendations.append(
            "OAuth governance: Review and revoke unnecessary app consents. "
            "Implement app consent policies to prevent users from granting broad permissions. "
            "For Copilot plugins, only allow verified publishers and review permission scopes. "
            "Monitor OAuth grant logs for suspicious patterns (e.g., Mail.ReadWrite + Files.ReadWrite.All)."
        )
    
    # Build observation with data source info
    data_source_note = ""
    if data_sources_missing:
        data_source_note = (
            f"\n\n**ℹ️ Partial Analysis** - Using {len(data_sources_used)} of 2 data sources:\n" +
            "  ✅ " + "\n  ✅ ".join(data_sources_used) + "\n" +
            "  ❌ " + "\n  ❌ ".join(data_sources_missing) +
            "\n\nFor complete threat detection, onboard devices to enable Advanced Hunting."
        )
    
    if threat_count == 0:
        status = "Success"
        importance = "Low"
        base_obs = (
            "**No significant Copilot-related threats detected** in available data sources."
        )
        if has_defender_api:
            base_obs += (
                "\n\nAdvanced Hunting analysis shows clean telemetry for:"
                "\n  - Process execution patterns (no suspicious automation)"
                "\n  - Network activity (normal Copilot usage)"
                "\n  - File access patterns (no unusual sensitive data access)"
                "\n  - Email threats (no AI-themed phishing)"
                "\n  - Identity risks (no compromised accounts)"
                "\n  - OAuth apps (no high-risk third-party integrations)"
            )
        else:
            base_obs += (
                "\n\nGraph Security analysis shows:"
                "\n  - Identity risks (no compromised accounts detected)"
                "\n  - OAuth apps (no high-risk third-party integrations detected)"
                "\n\nNote: Limited to cloud-side threat detection without device telemetry."
            )
        observation = base_obs + data_source_note
        recommendation = (
            "Maintain continuous monitoring. Review alerts regularly for Copilot anomalies. "
            "Stay updated with Defender Threat Intelligence."
        )
    elif threat_count >= 3:
        status = "Critical"
        importance = "High"  # Map Critical to High priority
        observation = (
            f"**{threat_count} active threats** targeting Copilot:\n\n" +
            "\n\n".join(threats_detected[:3]) +  # Top 3 threats only
            data_source_note
        )
        recommendation = "\n\n".join(recommendations[:2])  # Top 2 recommendations
    else:
        status = "Warning"
        importance = "High"
        observation = (
            f"**{threat_count} threat(s)** involving Copilot:\n\n" +
            "\n\n".join(threats_detected) +
            data_source_note
        )
        recommendation = "\n\n".join(recommendations)
    
    return new_recommendation(
        service="Defender",
        feature="Copilot Threat Intelligence",
        status=status,
        observation=observation,
        recommendation=recommendation,
        priority=importance,
        link_text="Advanced Hunting for Copilot",
        link_url="https://learn.microsoft.com/microsoft-365/security/defender/advanced-hunting-microsoft-365-copilot"
    )
