"""
Microsoft Entra ID P1 - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Entra ID P1 provides advanced identity management including
    Conditional Access required for secure Copilot deployment.
    
    When entra_insights is provided, enriches observations with:
    - Conditional Access policy metrics
    - MFA enrollment and usage metrics
    - Sign-in analytics and legacy authentication detection
    """
    feature_name = "Microsoft Entra ID P1"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # Cache metrics dictionaries (empty if entra_insights not available)
    ca_metrics = {}
    mfa_metrics = {}
    signin_metrics = {}
    
    if status == "Success":
        # Base observation for license check
        observation = f"{feature_name} is active in {friendly_sku}, providing advanced identity capabilities for Copilot security"
        recommendation_text = ""
        
        # Enrich with metrics when entra_insights is available
        if entra_insights and entra_insights.get('available'):
            # Populate metrics dictionaries to avoid redundant lookups
            ca_metrics = entra_insights.get('ca_metrics', {})
            mfa_metrics = entra_insights.get('mfa_metrics', {})
            signin_metrics = entra_insights.get('signin_metrics', {})
            
            metrics = []
            
            # Conditional Access metrics - only show positive findings
            if ca_metrics.get('total_policies', 0) > 0:
                metrics.append(f"{ca_metrics['total_policies']} Conditional Access policy(ies) configured")
            
            # MFA metrics - only show positive findings
            if mfa_metrics.get('mfa_enabled_users', 0) > 0:
                metrics.append(f"{mfa_metrics['mfa_enabled_users']} user(s) enrolled in MFA")
            
            if metrics:
                observation += ". " + ", ".join(metrics)
            
            # Generate proactive recommendations based on findings
            recommendation_text = entra_insights.get('ca_recommendation', '')
        
        # Primary license check observation
        recommendations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=observation,
            recommendation=recommendation_text,
            link_text="Identity Foundation for AI",
            link_url="https://learn.microsoft.com/entra/identity/",
            status=status
        ))
        
        # Additional observations when entra_insights is available
        if entra_insights and entra_insights.get('available'):
            # Observation 1: Conditional Access policy coverage
            total_policies = ca_metrics.get('total_policies', 0)
            copilot_policies = ca_metrics.get('copilot_policies', 0)
            
            if total_policies == 0:
                # Action Required: No CA policies
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="No Conditional Access policies configured, leaving Copilot access unprotected",
                    recommendation="Implement Conditional Access policies to protect Copilot access. Start with requiring MFA for all users, blocking legacy authentication, and enforcing device compliance. CA policies are essential for preventing unauthorized AI usage and protecting sensitive data accessed through Copilot.",
                    link_text="Configure Conditional Access",
                    link_url="https://learn.microsoft.com/entra/identity/conditional-access/overview",
                    priority="High",
                    status="Action Required"
                ))
            elif copilot_policies == 0:
                # Action Required: No Copilot-specific policies
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{total_policies} Conditional Access policy(ies) configured, but none specifically target Copilot applications",
                    recommendation="Create Copilot-specific Conditional Access policies targeting Microsoft 365 Copilot and Graph Connector applications. Apply stricter controls for AI access: require compliant devices, trusted locations, and MFA. Consider blocking Copilot access from unmanaged devices to prevent data exfiltration.",
                    link_text="Conditional Access for Copilot",
                    link_url="https://learn.microsoft.com/entra/identity/conditional-access/concept-conditional-access-cloud-apps",
                    priority="Medium",
                    status="Action Required"
                ))
            else:
                # Success: Copilot policies configured
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{copilot_policies} Conditional Access policy(ies) protecting Copilot applications",
                    recommendation="",
                    link_text="Conditional Access Best Practices",
                    link_url="https://learn.microsoft.com/entra/identity/conditional-access/plan-conditional-access",
                    status="Success"
                ))
            
            # Observation 2: MFA enrollment and usage
            total_users = mfa_metrics.get('total_users', 0)
            mfa_enabled = mfa_metrics.get('mfa_enabled_users', 0)
            mfa_percentage = (mfa_enabled / total_users * 100) if total_users > 0 else 0
            
            if mfa_percentage < 50:
                # Action Required: Low MFA adoption
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"Only {mfa_enabled} of {total_users} users ({mfa_percentage:.1f}%) enrolled in MFA, exposing Copilot to credential theft",
                    recommendation="Enforce MFA registration for all users accessing Copilot. Use Conditional Access to require MFA for Microsoft 365 apps. Compromised accounts without MFA can access Copilot to exfiltrate organizational data through AI prompts. Aim for 100% MFA coverage.",
                    link_text="Configure MFA Requirements",
                    link_url="https://learn.microsoft.com/entra/identity/authentication/howto-mfa-getstarted",
                    priority="High",
                    status="Action Required"
                ))
            elif mfa_percentage < 90:
                # Action Required: Moderate MFA adoption
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{mfa_enabled} of {total_users} users ({mfa_percentage:.1f}%) enrolled in MFA, approaching secure coverage for Copilot access",
                    recommendation=f"Continue rolling out MFA to remaining {total_users - mfa_enabled} users. Use Conditional Access to require MFA for all Copilot and Microsoft 365 access. Target 100% MFA coverage to fully protect AI services from compromised credentials.",
                    link_text="MFA Deployment Guide",
                    link_url="https://learn.microsoft.com/entra/identity/authentication/howto-mfa-getstarted",
                    priority="Medium",
                    status="Action Required"
                ))
            else:
                # Success: High MFA adoption
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{mfa_enabled} of {total_users} users ({mfa_percentage:.1f}%) enrolled in MFA, strongly protecting Copilot access",
                    recommendation="",
                    link_text="MFA Best Practices",
                    link_url="https://learn.microsoft.com/entra/identity/authentication/concept-mfa-howitworks",
                    status="Success"
                ))
            
            # Observation 3: Legacy authentication detection
            legacy_auth_count = signin_metrics.get('legacy_auth_sign_ins', 0)
            
            if legacy_auth_count > 0:
                # Action Required: Legacy auth detected
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{legacy_auth_count} legacy authentication sign-in(s) detected in the past 30 days, bypassing MFA and CA protections",
                    recommendation="Block legacy authentication protocols (IMAP, POP3, SMTP AUTH) using Conditional Access. Legacy auth bypasses MFA and cannot be protected by Conditional Access policies, creating a backdoor for attackers to access Copilot. Migrate apps to modern authentication (OAuth 2.0) and block legacy protocols tenant-wide.",
                    link_text="Block Legacy Authentication",
                    link_url="https://learn.microsoft.com/entra/identity/conditional-access/block-legacy-authentication",
                    priority="High",
                    status="Action Required"
                ))
            else:
                # Success: No legacy auth
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="No legacy authentication sign-ins detected, all access uses modern authentication with full security controls",
                    recommendation="",
                    link_text="Modern Authentication Overview",
                    link_url="https://learn.microsoft.com/microsoft-365/enterprise/hybrid-modern-auth-overview",
                    status="Success"
                ))
            
            # Observation 4: Passwordless authentication adoption
            auth_metrics = entra_insights.get('auth_summary', {})
            if auth_metrics:
                # Get method breakdown from nested structure
                methods = auth_metrics.get('methods', {})
                fido2_users = methods.get('fido2', 0)
                windows_hello_users = methods.get('windowsHello', 0)
                authenticator_users = methods.get('microsoftAuthenticator', 0)
                total_passwordless = fido2_users + windows_hello_users + authenticator_users
                passwordless_rate = auth_metrics.get('passwordless_adoption_rate', 0)
                
                # Build method breakdown text
                method_details = []
                if fido2_users > 0:
                    method_details.append(f"{fido2_users} FIDO2")
                if windows_hello_users > 0:
                    method_details.append(f"{windows_hello_users} Windows Hello")
                if authenticator_users > 0:
                    method_details.append(f"{authenticator_users} Authenticator app")
                method_text = f" ({', '.join(method_details)})" if method_details else ""
                
                if passwordless_rate < 10:
                    # Action Required: Very low passwordless adoption
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"Only {passwordless_rate:.1f}% of users ({total_passwordless}{method_text}) use passwordless authentication, leaving Copilot vulnerable to password attacks",
                        recommendation="Deploy passwordless authentication (FIDO2 security keys, Windows Hello for Business, or Microsoft Authenticator app) to eliminate password-based attacks targeting Copilot access. Passwordless methods are phishing-resistant and significantly reduce credential theft risks. Use Conditional Access to require passwordless auth for high-value resources like Copilot. Start with pilot groups and expand based on user feedback.",
                        link_text="Deploy Passwordless Authentication",
                        link_url="https://learn.microsoft.com/entra/identity/authentication/concept-authentication-passwordless",
                        priority="Medium",
                        status="Action Required"
                    ))
                elif passwordless_rate < 50:
                    # Action Required: Moderate passwordless adoption
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"{passwordless_rate:.1f}% of users ({total_passwordless}{method_text}) use passwordless authentication, making progress toward phishing-resistant Copilot access",
                        recommendation=f"Continue passwordless rollout to reach 80%+ adoption. Focus on eliminating password-based authentication for Copilot users. Use Temporary Access Pass (TAP) to onboard users to Windows Hello or FIDO2. Consider requiring passwordless for executives and high-risk users accessing sensitive AI capabilities.",
                        link_text="Passwordless Deployment Guide",
                        link_url="https://learn.microsoft.com/entra/identity/authentication/howto-authentication-passwordless-deployment",
                        priority="Medium",
                        status="Action Required"
                    ))
                else:
                    # Success: High passwordless adoption
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"{passwordless_rate:.1f}% of users ({total_passwordless}{method_text}) use passwordless authentication, providing phishing-resistant protection for Copilot",
                        recommendation="",
                        link_text="Passwordless Best Practices",
                        link_url="https://learn.microsoft.com/entra/identity/authentication/concept-authentication-passwordless",
                        status="Success"
                    ))
            
            # Observation 5: Group-based licensing for Copilot
            group_metrics = entra_insights.get('group_licensing_summary', {})
            if group_metrics:
                total_license_groups = group_metrics.get('total_groups_with_licenses', 0)
                copilot_groups = group_metrics.get('copilot_license_groups', 0)
                dynamic_groups = group_metrics.get('dynamic_groups', 0)
                groups_with_errors = group_metrics.get('groups_with_errors', 0)
                
                if copilot_groups == 0 and total_license_groups == 0:
                    # Action Required: No group-based licensing
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation="No group-based licensing configured - Copilot licenses likely assigned manually to individual users",
                        recommendation="Implement group-based licensing to automate Copilot license assignment and improve governance. Manual license assignment: 1) Creates administrative overhead for every new Copilot user, 2) Increases risk of orphaned licenses when users leave, 3) Lacks audit trail for compliance, 4) Cannot leverage dynamic groups for role-based access. Create security groups for Copilot users (e.g., 'Copilot-Sales', 'Copilot-Finance') and assign M365 licenses to groups. Use dynamic groups with rules like 'department equals Sales' to automatically assign/remove licenses based on user attributes. Configure license inheritance to cascade Copilot access to nested groups. This enables self-service access (users get Copilot when added to group), improves license reclamation, and provides clear governance model.",
                        link_text="Group-Based Licensing",
                        link_url="https://learn.microsoft.com/entra/identity/users/licensing-groups-assign",
                        priority="Medium",
                        status="Action Required"
                    ))
                elif copilot_groups == 0:
                    # Action Required: Group licensing exists but not for Copilot
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"{total_license_groups} group(s) use license assignment, but none configured for Copilot licenses",
                        recommendation=f"Extend group-based licensing to Copilot license management. You have {dynamic_groups} dynamic group(s) - leverage these for automated Copilot access. Create dedicated groups for Copilot users by department, role, or project. Benefits: 1) Automatic license assignment when users join groups, 2) Automatic removal when users transfer/leave, 3) Clear audit trail for compliance reviews, 4) Simplified license optimization and cost management. Start with pilot group for early adopters, then expand based on business units.",
                        link_text="Assign Copilot Licenses to Groups",
                        link_url="https://learn.microsoft.com/entra/identity/users/licensing-groups-assign",
                        priority="Medium",
                        status="Action Required"
                    ))
                elif groups_with_errors > 0:
                    # Action Required: License assignment errors
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"{copilot_groups} group(s) configured for Copilot licensing, but {groups_with_errors} group(s) have license assignment errors",
                        recommendation=f"Resolve license assignment errors in {groups_with_errors} group(s) to ensure users receive Copilot access. Common errors: 1) Insufficient licenses available (purchase more or remove inactive users), 2) Conflicting service plans (resolve by disabling conflicting features), 3) Duplicate assignments (user in multiple groups with same license), 4) Usage location not set (required for license assignment). Review errors in Azure AD > Groups > Licenses tab and remediate. Ensure all Copilot users have usage location configured and sufficient licenses are available.",
                        link_text="Troubleshoot Group Licensing",
                        link_url="https://learn.microsoft.com/entra/identity/users/licensing-groups-resolve-problems",
                        priority="High",
                        status="Action Required"
                    ))
                else:
                    # Success: Group-based licensing active
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"{copilot_groups} group(s) manage Copilot license assignment ({dynamic_groups} dynamic), automating access governance",
                        recommendation="",
                        link_text="Group-Based Licensing Best Practices",
                        link_url="https://learn.microsoft.com/entra/identity/users/licensing-groups-assign",
                        status="Success"
                    ))
        
        return recommendations
    
    # Non-Success: Keep original license-check recommendation unchanged
    return new_recommendation(
        service="Entra",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, missing critical identity features for AI governance",
        recommendation=f"Enable {feature_name} to access Conditional Access, group-based licensing, self-service password reset, and advanced identity protection required for Copilot governance. P1 enables context-aware policies that restrict Copilot based on user risk, device compliance, and location - essential for securing AI access. Use dynamic groups to automate Copilot license assignment, simplify access management, and ensure only authorized users can leverage AI capabilities. P1 is the minimum identity tier recommended for enterprise Copilot deployments.",
        link_text="Identity Foundation for AI",
        link_url="https://learn.microsoft.com/entra/identity/",
        priority="High",
        status=status
    )

