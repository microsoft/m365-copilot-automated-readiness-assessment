"""
Entra Insights - Pre-computed identity & security metrics from Entra client
Similar to pp_insights and defender_insights patterns
"""

def extract_entra_insights_from_client(entra_client):
    """
    Extract Entra identity & security insights from cached client data.
    Call this ONCE and reuse the result across all recommendations to avoid redundant processing.
    
    Args:
        entra_client: EntraClient object with cached API data
    
    Returns:
        dict with pre-computed metrics for all 11 enhanced observations
    """
    if not entra_client or not entra_client.available:
        return {
            'available': False,
            
            # Conditional Access
            'ca_total': 0,
            'ca_enabled': 0,
            'ca_require_mfa': 0,
            'ca_require_compliant_device': 0,
            'ca_target_m365': 0,
            'ca_block_legacy_auth': 0,
            'ca_user_risk_based': 0,
            'ca_signin_risk_based': 0,
            
            # MFA & Authentication
            'total_users': 0,
            'mfa_registered': 0,
            'mfa_registration_rate': 0,
            'passwordless_enabled': 0,
            'passwordless_adoption_rate': 0,
            'fido2_users': 0,
            'windows_hello_users': 0,
            'authenticator_users': 0,
            'legacy_auth_attempts': 0,
            
            # Identity Protection
            'risky_users_total': 0,
            'risky_users_high': 0,
            'confirmed_compromised': 0,
            'user_risk_policy_exists': False,
            'signin_risk_policy_exists': False,
            'risk_detections_total': 0,
            
            # PIM
            'permanent_assignments': 0,
            'permanent_global_admins': 0,
            'eligible_assignments': 0,
            'pim_enabled_roles': 0,
            'time_bound_assignments': 0,
            
            # Access Reviews
            'access_review_total': 0,
            'active_reviews': 0,
            'group_reviews': 0,
            'role_reviews': 0,
            'guest_reviews': 0,
            'recurring_reviews': 0,
            
            # Device Compliance
            'total_managed_devices': 0,
            'compliant_devices': 0,
            'non_compliant_devices': 0,
            'compliance_rate': 0,
            'corporate_owned': 0,
            'byod_devices': 0,
            'compliance_policies': 0,
            'ca_requires_compliance': False,
            
            # Group-Based Licensing
            'groups_with_licenses': 0,
            'copilot_license_groups': 0,
            'dynamic_groups': 0,
            'groups_with_errors': 0,
            
            # B2B Collaboration
            'total_guests': 0,
            'guests_with_licenses': 0,
            'cross_tenant_configured': False,
            'guest_invite_restrictions': 'Unknown',
            
            # App Consent
            'total_apps': 0,
            'user_consent_allowed': False,
            'admin_consent_required': False,
            'high_privilege_apps': 0,
            'apps_with_graph_access': 0,
            'unverified_publishers': 0,
            
            # Sign-in Logs
            'total_signins_sampled': 0,
            'mfa_success_rate': 0,
            'ca_failure_count': 0,
            'risky_signins': 0
        }
    
    # Extract from pre-computed summaries (no API calls - already cached!)
    ca_summary = getattr(entra_client, 'ca_summary', {})
    auth_summary = getattr(entra_client, 'auth_summary', {})
    risk_summary = getattr(entra_client, 'risk_summary', {})
    pim_summary = getattr(entra_client, 'pim_summary', {})
    access_review_summary = getattr(entra_client, 'access_review_summary', {})
    device_summary = getattr(entra_client, 'device_summary', {})
    group_summary = getattr(entra_client, 'group_licensing_summary', {})
    b2b_summary = getattr(entra_client, 'b2b_summary', {})
    consent_summary = getattr(entra_client, 'consent_summary', {})
    signin_summary = getattr(entra_client, 'signin_summary', {})
    network_access_summary = getattr(entra_client, 'network_access_summary', {})
    private_access_summary = getattr(entra_client, 'private_access_summary', {})
    
    # Calculate derived metrics
    total_devices = device_summary.get('total_managed', 0)
    compliant = device_summary.get('compliant', 0)
    compliance_rate = int((compliant / total_devices * 100)) if total_devices > 0 else 0
    
    # MFA success rate from sign-ins
    mfa_required = signin_summary.get('mfa_required', 0)
    mfa_success = signin_summary.get('mfa_success', 0)
    mfa_success_rate = int((mfa_success / mfa_required * 100)) if mfa_required > 0 else 0
    
    return {
        'available': True,
        
        # Conditional Access (#4)
        'ca_total': ca_summary.get('total', 0),
        'ca_enabled': ca_summary.get('enabled', 0),
        'ca_report_only': ca_summary.get('report_only', 0),
        'ca_disabled': ca_summary.get('disabled', 0),
        'ca_require_mfa': ca_summary.get('require_mfa', 0),
        'ca_require_compliant_device': ca_summary.get('require_compliant_device', 0),
        'ca_require_managed_device': ca_summary.get('require_managed_device', 0),
        'ca_target_m365': ca_summary.get('target_m365_apps', 0),
        'ca_target_all_apps': ca_summary.get('target_all_apps', 0),
        'ca_block_legacy_auth': ca_summary.get('block_legacy_auth', 0),
        'ca_location_based': ca_summary.get('location_based', 0),
        'ca_user_risk_based': ca_summary.get('user_risk_based', 0),
        'ca_signin_risk_based': ca_summary.get('signin_risk_based', 0),
        
        # MFA & Authentication (#3, #10)
        'total_users': auth_summary.get('total_users', 0),
        'mfa_registered': auth_summary.get('mfa_registered', 0),
        'mfa_capable': auth_summary.get('mfa_capable', 0),
        'mfa_registration_rate': auth_summary.get('mfa_registration_rate', 0),
        'passwordless_enabled': auth_summary.get('passwordless_enabled', 0),
        'passwordless_adoption_rate': auth_summary.get('passwordless_adoption_rate', 0),
        'fido2_users': auth_summary.get('methods', {}).get('fido2', 0),
        'windows_hello_users': auth_summary.get('methods', {}).get('windowsHello', 0),
        'authenticator_users': auth_summary.get('methods', {}).get('microsoftAuthenticator', 0),
        'phone_users': auth_summary.get('methods', {}).get('phone', 0),
        'email_users': auth_summary.get('methods', {}).get('email', 0),
        'legacy_auth_attempts': signin_summary.get('legacy_auth_attempts', 0),
        
        # Identity Protection (#1, #5)
        'risky_users_total': risk_summary.get('risky_users_total', 0),
        'risky_users_high': risk_summary.get('risky_users_high', 0),
        'risky_users_medium': risk_summary.get('risky_users_medium', 0),
        'risky_users_low': risk_summary.get('risky_users_low', 0),
        'confirmed_compromised': risk_summary.get('confirmed_compromised', 0),
        'at_risk': risk_summary.get('at_risk', 0),
        'remediated': risk_summary.get('remediated', 0),
        'dismissed': risk_summary.get('dismissed', 0),
        'risk_detections_total': risk_summary.get('risk_detections_total', 0),
        'risk_detections_high': risk_summary.get('risk_detections_high', 0),
        'user_risk_policy_exists': risk_summary.get('user_risk_policy_exists', False),
        'signin_risk_policy_exists': risk_summary.get('signin_risk_policy_exists', False),
        
        # Privileged Identity Management (#1, #8)
        'total_active_assignments': pim_summary.get('total_active_assignments', 0),
        'total_eligible_assignments': pim_summary.get('total_eligible_assignments', 0),
        'permanent_assignments': pim_summary.get('permanent_assignments', 0),
        'permanent_global_admins': pim_summary.get('permanent_global_admins', 0),
        'permanent_privileged_roles': pim_summary.get('permanent_privileged_roles', 0),
        'eligible_assignments': pim_summary.get('eligible_assignments', 0),
        'pim_enabled_roles': pim_summary.get('pim_enabled_roles', 0),
        'time_bound_assignments': pim_summary.get('total_time_bound_assignments', 0),
        'roles_with_only_permanent': pim_summary.get('roles_with_only_permanent', 0),
        
        # Access Reviews (#1, #9)
        'access_review_total': access_review_summary.get('total_definitions', 0),
        'active_reviews': access_review_summary.get('active_reviews', 0),
        'group_reviews': access_review_summary.get('group_membership_reviews', 0),
        'role_reviews': access_review_summary.get('role_assignment_reviews', 0),
        'app_reviews': access_review_summary.get('application_assignment_reviews', 0),
        'guest_reviews': access_review_summary.get('guest_user_reviews', 0),
        'recurring_reviews': access_review_summary.get('recurring_reviews', 0),
        'one_time_reviews': access_review_summary.get('one_time_reviews', 0),
        
        # Device Compliance (#2, #7)
        'total_managed_devices': total_devices,
        'compliant_devices': compliant,
        'non_compliant_devices': device_summary.get('non_compliant', 0),
        'in_grace_period': device_summary.get('in_grace_period', 0),
        'compliance_rate': compliance_rate,
        'corporate_owned': device_summary.get('corporate_owned', 0),
        'byod_devices': device_summary.get('personal_byod', 0),
        'windows_devices': device_summary.get('windows', 0),
        'ios_devices': device_summary.get('ios', 0),
        'android_devices': device_summary.get('android', 0),
        'macos_devices': device_summary.get('macos', 0),
        'compliance_policies': device_summary.get('compliance_policies_total', 0),
        'ca_requires_compliance': device_summary.get('ca_requires_compliance', False),
        
        # Group-Based Licensing (#2)
        'groups_with_licenses': group_summary.get('total_groups_with_licenses', 0),
        'copilot_license_groups': group_summary.get('copilot_license_groups', 0),
        'dynamic_groups': group_summary.get('dynamic_groups', 0),
        'groups_with_errors': group_summary.get('groups_with_errors', 0),
        'total_license_errors': group_summary.get('total_license_errors', 0),
        
        # B2B Collaboration (#6)
        'total_guests': b2b_summary.get('total_guests', 0),
        'guests_with_licenses': b2b_summary.get('guests_with_licenses', 0),
        'cross_tenant_configured': b2b_summary.get('cross_tenant_access_configured', False),
        'guest_invite_restrictions': b2b_summary.get('guest_invite_restrictions', 'Unknown'),
        'partner_configurations': b2b_summary.get('partner_configurations', 0),
        
        # Application Consent (#11)
        'total_apps': consent_summary.get('total_apps', 0),
        'user_consent_allowed': consent_summary.get('user_consent_allowed', False),
        'admin_consent_required': consent_summary.get('admin_consent_required', False),
        'high_privilege_apps': consent_summary.get('high_privilege_apps', 0),
        'apps_with_graph_access': consent_summary.get('apps_with_graph_access', 0),
        'apps_with_mail_access': consent_summary.get('apps_with_mail_access', 0),
        'apps_with_files_access': consent_summary.get('apps_with_files_access', 0),
        'apps_with_delegated_perms': consent_summary.get('apps_with_delegated_permissions', 0),
        'unverified_publishers': consent_summary.get('unverified_publishers', 0),
        
        # Sign-in Activity (used across multiple observations)
        'total_signins_sampled': signin_summary.get('total_signins_sampled', 0),
        'mfa_success_rate': mfa_success_rate,
        'ca_success': signin_summary.get('ca_success', 0),
        'ca_failure': signin_summary.get('ca_failure', 0),
        'failed_signins': signin_summary.get('failed_signins', 0),
        'risky_signins': signin_summary.get('risky_signins', 0),
        
        # Nested dictionaries for recommendation modules (AAD_PREMIUM_P2, AAD_PREMIUM_P1)
        'pim_metrics': {
            'permanent_admins_count': pim_summary.get('permanent_assignments', 0),
            'eligible_admins_count': pim_summary.get('eligible_assignments', 0),
            'permanent_global_admins': pim_summary.get('permanent_global_admins', 0),
            'pim_enabled_roles': pim_summary.get('pim_enabled_roles', 0)
        },
        'access_review_metrics': {
            'total_active_reviews': access_review_summary.get('active_reviews', 0),
            'total_definitions': access_review_summary.get('total_definitions', 0),
            'group_reviews': access_review_summary.get('group_membership_reviews', 0),
            'role_reviews': access_review_summary.get('role_assignment_reviews', 0),
            'guest_reviews': access_review_summary.get('guest_user_reviews', 0),
            'recurring_reviews': access_review_summary.get('recurring_reviews', 0)
        },
        'risk_metrics': {
            'high_risk_users': risk_summary.get('risky_users_high', 0),
            'medium_risk_users': risk_summary.get('risky_users_medium', 0),
            'low_risk_users': risk_summary.get('risky_users_low', 0),
            'total_risky_users': risk_summary.get('risky_users_total', 0),
            'confirmed_compromised': risk_summary.get('confirmed_compromised', 0)
        },
        'ca_metrics': {
            'total_policies': ca_summary.get('total', 0),
            'enabled_policies': ca_summary.get('enabled', 0),
            'copilot_policies': ca_summary.get('target_m365_apps', 0),
            'require_mfa': ca_summary.get('require_mfa', 0),
            'require_compliant_device': ca_summary.get('require_compliant_device', 0),
            'block_legacy_auth': ca_summary.get('block_legacy_auth', 0)
        },
        'mfa_metrics': {
            'total_users': auth_summary.get('total_users', 0),
            'mfa_enabled_users': auth_summary.get('mfa_registered', 0),
            'mfa_capable_users': auth_summary.get('mfa_capable', 0),
            'mfa_registration_rate': auth_summary.get('mfa_registration_rate', 0),
            'passwordless_users': auth_summary.get('passwordless_enabled', 0),
            'fido2_users': auth_summary.get('methods', {}).get('fido2', 0),
            'windows_hello_users': auth_summary.get('methods', {}).get('windowsHello', 0)
        },
        'signin_metrics': {
            'total_signins': signin_summary.get('total_signins_sampled', 0),
            'legacy_auth_sign_ins': signin_summary.get('legacy_auth_attempts', 0),
            'mfa_success_rate': mfa_success_rate,
            'ca_failures': signin_summary.get('ca_failure', 0),
            'risky_signins': signin_summary.get('risky_signins', 0),
            'failed_signins': signin_summary.get('failed_signins', 0)
        },
        'network_access_summary': {
            'status': network_access_summary.get('status', 'Success'),
            'error': network_access_summary.get('error'),
            'enabled': network_access_summary.get('enabled', False),
            'total_filtering_policies': network_access_summary.get('total_filtering_policies', 0),
            'total_forwarding_profiles': network_access_summary.get('total_forwarding_profiles', 0),
            'web_filtering_enabled': network_access_summary.get('web_filtering_enabled', False),
            'traffic_forwarding_enabled': network_access_summary.get('traffic_forwarding_enabled', False),
            'fqdn_rules_count': network_access_summary.get('fqdn_rules_count', 0),
            'web_category_rules_count': network_access_summary.get('web_category_rules_count', 0),
            'm365_traffic_forwarding': network_access_summary.get('m365_traffic_forwarding', False),
            'internet_traffic_forwarding': network_access_summary.get('internet_traffic_forwarding', False)
        },
        'private_access_summary': {
            'status': private_access_summary.get('status', 'Success'),
            'error': private_access_summary.get('error'),
            'enabled': private_access_summary.get('enabled', False),
            'total_connectors': private_access_summary.get('total_connectors', 0),
            'active_connectors': private_access_summary.get('active_connectors', 0),
            'total_apps': private_access_summary.get('total_apps', 0),
            'apps_with_quick_access': private_access_summary.get('apps_with_quick_access', 0),
            'apps_with_per_app_access': private_access_summary.get('apps_with_per_app_access', 0)
        },
        'device_summary': {
            'total_managed_devices': total_devices,
            'compliant_devices': compliant,
            'non_compliant_devices': device_summary.get('non_compliant', 0),
            'ca_requires_compliance': device_summary.get('ca_requires_compliance', False)
        },
        
        # Additional nested summaries for new observations
        'auth_summary': {
            'passwordless_adoption_rate': auth_summary.get('passwordless_adoption_rate', 0),
            'methods': {
                'fido2': auth_summary.get('methods', {}).get('fido2', 0),
                'windowsHello': auth_summary.get('methods', {}).get('windowsHello', 0),
                'microsoftAuthenticator': auth_summary.get('methods', {}).get('microsoftAuthenticator', 0),
                'phone': auth_summary.get('methods', {}).get('phone', 0),
                'email': auth_summary.get('methods', {}).get('email', 0)
            }
        },
        'b2b_summary': {
            'total_guests': b2b_summary.get('total_guests', 0),
            'guests_with_licenses': b2b_summary.get('guests_with_licenses', 0),
            'guest_invite_restrictions': b2b_summary.get('guest_invite_restrictions', 'Unknown'),
            'cross_tenant_access_configured': b2b_summary.get('cross_tenant_access_configured', False),
            'partner_configurations': b2b_summary.get('partner_configurations', 0)
        },
        'consent_summary': {
            'user_consent_allowed': consent_summary.get('user_consent_allowed', False),
            'admin_consent_required': consent_summary.get('admin_consent_required', False),
            'high_privilege_apps': consent_summary.get('high_privilege_apps', 0),
            'unverified_publishers': consent_summary.get('unverified_publishers', 0),
            'apps_with_graph_access': consent_summary.get('apps_with_graph_access', 0),
            'apps_with_mail_access': consent_summary.get('apps_with_mail_access', 0),
            'apps_with_files_access': consent_summary.get('apps_with_files_access', 0)
        },
        'group_licensing_summary': {
            'total_groups_with_licenses': group_summary.get('total_groups_with_licenses', 0),
            'copilot_license_groups': group_summary.get('copilot_license_groups', 0),
            'dynamic_groups': group_summary.get('dynamic_groups', 0),
            'groups_with_errors': group_summary.get('groups_with_errors', 0)
        },
        'access_review_summary': {
            'total_definitions': access_review_summary.get('total_definitions', 0),
            'active_reviews': access_review_summary.get('active_reviews', 0),
            'group_reviews': access_review_summary.get('group_membership_reviews', 0),
            'role_reviews': access_review_summary.get('role_assignment_reviews', 0),
            'guest_reviews': access_review_summary.get('guest_user_reviews', 0),
            'recurring_reviews': access_review_summary.get('recurring_reviews', 0)
        }
    }


# Helper functions for building observations (similar to defender_insights pattern)

def build_ca_metrics(entra_insights):
    """
    Build Conditional Access metrics text for observations.
    Returns: list of metric strings
    """
    if not entra_insights or not entra_insights.get('available'):
        return []
    
    metrics = []
    
    total = entra_insights.get('ca_total', 0)
    if total > 0:
        metrics.append(f"{total} CA policies")
        
        enabled = entra_insights.get('ca_enabled', 0)
        if enabled > 0:
            metrics.append(f"{enabled} enabled")
        
        require_mfa = entra_insights.get('ca_require_mfa', 0)
        if require_mfa > 0:
            metrics.append(f"{require_mfa} require MFA")
        
        target_m365 = entra_insights.get('ca_target_m365', 0)
        if target_m365 > 0:
            metrics.append(f"{target_m365} target M365 apps")
    
    return metrics


def build_mfa_metrics(entra_insights):
    """
    Build MFA & authentication metrics text for observations.
    Returns: list of metric strings
    """
    if not entra_insights or not entra_insights.get('available'):
        return []
    
    metrics = []
    
    reg_rate = entra_insights.get('mfa_registration_rate', 0)
    if reg_rate > 0:
        metrics.append(f"{reg_rate}% MFA registered")
    
    passwordless_rate = entra_insights.get('passwordless_adoption_rate', 0)
    if passwordless_rate > 0:
        metrics.append(f"{passwordless_rate}% passwordless")
    
    legacy = entra_insights.get('legacy_auth_attempts', 0)
    if legacy > 0:
        metrics.append(f"{legacy} legacy auth attempts")
    
    return metrics


def build_risk_metrics(entra_insights):
    """
    Build Identity Protection risk metrics text for observations.
    Returns: (metrics_list, recommendation_text)
    """
    if not entra_insights or not entra_insights.get('available'):
        return [], ""
    
    metrics = []
    recommendation = ""
    
    risky_total = entra_insights.get('risky_users_total', 0)
    risky_high = entra_insights.get('risky_users_high', 0)
    compromised = entra_insights.get('confirmed_compromised', 0)
    
    if risky_total > 0:
        if compromised > 0:
            metrics.append(f"{risky_total} risky users ({compromised} compromised)")
            recommendation = f"Revoke access for {compromised} compromised account(s)"
        elif risky_high > 0:
            metrics.append(f"{risky_total} risky users ({risky_high} high-risk)")
            recommendation = f"Review {risky_high} high-risk user(s)"
        else:
            metrics.append(f"{risky_total} risky users")
    
    # Add risk policy status
    user_policy = entra_insights.get('user_risk_policy_exists', False)
    signin_policy = entra_insights.get('signin_risk_policy_exists', False)
    
    if not user_policy and not signin_policy and not recommendation:
        recommendation = "Configure user risk and sign-in risk policies"
    
    return metrics, recommendation


def build_pim_metrics(entra_insights):
    """
    Build PIM metrics text for observations.
    Returns: (metrics_list, recommendation_text)
    """
    if not entra_insights or not entra_insights.get('available'):
        return [], ""
    
    metrics = []
    recommendation = ""
    
    permanent = entra_insights.get('permanent_assignments', 0)
    eligible = entra_insights.get('eligible_assignments', 0)
    global_admins = entra_insights.get('permanent_global_admins', 0)
    
    if permanent > 0:
        metrics.append(f"{permanent} permanent role assignments")
    if eligible > 0:
        metrics.append(f"{eligible} eligible (PIM) assignments")
    
    if global_admins > 0:
        metrics.append(f"{global_admins} permanent global admins")
        if global_admins > 5:
            recommendation = "Move global admins to PIM eligible roles (recommended max: 5 permanent)"
    
    if permanent > 0 and eligible == 0:
        recommendation = "Enable PIM for just-in-time privileged access"
    
    return metrics, recommendation


def build_access_review_metrics(entra_insights):
    """
    Build Access Review metrics text for observations.
    Returns: list of metric strings
    """
    if not entra_insights or not entra_insights.get('available'):
        return []
    
    metrics = []
    
    total = entra_insights.get('access_review_total', 0)
    if total > 0:
        metrics.append(f"{total} access review campaigns")
        
        recurring = entra_insights.get('recurring_reviews', 0)
        if recurring > 0:
            metrics.append(f"{recurring} recurring")
        
        guest = entra_insights.get('guest_reviews', 0)
        if guest > 0:
            metrics.append(f"{guest} for guests")
    
    return metrics


def build_device_metrics(entra_insights):
    """
    Build Device Compliance metrics text for observations.
    Returns: list of metric strings
    """
    if not entra_insights or not entra_insights.get('available'):
        return []
    
    metrics = []
    
    total = entra_insights.get('total_managed_devices', 0)
    if total > 0:
        metrics.append(f"{total} managed devices")
        
        compliance_rate = entra_insights.get('compliance_rate', 0)
        metrics.append(f"{compliance_rate}% compliant")
        
        non_compliant = entra_insights.get('non_compliant_devices', 0)
        if non_compliant > 0:
            metrics.append(f"{non_compliant} non-compliant")
    
    return metrics


def build_b2b_metrics(entra_insights):
    """
    Build B2B collaboration metrics text for observations.
    Returns: list of metric strings
    """
    if not entra_insights or not entra_insights.get('available'):
        return []
    
    metrics = []
    
    guests = entra_insights.get('total_guests', 0)
    if guests > 0:
        metrics.append(f"{guests} guest users")
        
        with_licenses = entra_insights.get('guests_with_licenses', 0)
        if with_licenses > 0:
            metrics.append(f"{with_licenses} with licenses")
    
    cross_tenant = entra_insights.get('cross_tenant_configured', False)
    if cross_tenant:
        metrics.append("Cross-tenant access configured")
    
    return metrics


def build_app_consent_metrics(entra_insights):
    """
    Build App Consent metrics text for observations.
    Returns: (metrics_list, recommendation_text)
    """
    if not entra_insights or not entra_insights.get('available'):
        return [], ""
    
    metrics = []
    recommendation = ""
    
    total = entra_insights.get('total_apps', 0)
    if total > 0:
        metrics.append(f"{total} applications")
        
        high_priv = entra_insights.get('high_privilege_apps', 0)
        if high_priv > 0:
            metrics.append(f"{high_priv} high-privilege")
            recommendation = f"Review {high_priv} high-privilege app(s)"
        
        unverified = entra_insights.get('unverified_publishers', 0)
        if unverified > 0:
            metrics.append(f"{unverified} unverified publishers")
    
    user_consent = entra_insights.get('user_consent_allowed', False)
    if user_consent:
        metrics.append("User consent enabled")
        if not recommendation:
            recommendation = "Consider requiring admin consent for sensitive permissions"
    
    return metrics, recommendation


def build_observation_with_metrics(base_text, metrics, clean_status_text=""):
    """
    Build observation text with metrics or clean status.
    Similar to defender_insights.build_observation()
    
    Args:
        base_text: Base observation (e.g., "Feature is active")
        metrics: List of metric strings
        clean_status_text: Text to show when no metrics (e.g., "No issues detected")
    
    Returns: Complete observation text
    """
    if metrics and len(metrics) > 0:
        return base_text + ". " + ", ".join(metrics)
    elif clean_status_text:
        return base_text + ". " + clean_status_text
    else:
        return base_text


def get_ca_recommendation(entra_insights):
    """
    Generate smart CA policy recommendations based on insights.
    Returns: recommendation text or empty string
    """
    if not entra_insights or not entra_insights.get('available'):
        return ""
    
    recommendations = []
    
    total = entra_insights.get('ca_total', 0)
    if total == 0:
        return "Configure Conditional Access policies to secure M365 Copilot access with MFA and device compliance"
    
    target_m365 = entra_insights.get('ca_target_m365', 0)
    if target_m365 == 0:
        recommendations.append("Create CA policy targeting M365 apps for Copilot security")
    
    require_mfa = entra_insights.get('ca_require_mfa', 0)
    if require_mfa == 0:
        recommendations.append("Enable MFA requirement in CA policies")
    
    require_device = entra_insights.get('ca_require_compliant_device', 0)
    if require_device == 0:
        recommendations.append("Require compliant devices for Copilot access")
    
    return "; ".join(recommendations) if recommendations else ""


def get_passwordless_recommendation(entra_insights):
    """
    Generate passwordless adoption recommendations based on insights.
    Returns: recommendation text or empty string
    """
    if not entra_insights or not entra_insights.get('available'):
        return ""
    
    adoption_rate = entra_insights.get('passwordless_adoption_rate', 0)
    
    if adoption_rate == 0:
        return "Enable passwordless authentication (FIDO2, Windows Hello, Authenticator) for better Copilot UX"
    elif adoption_rate < 50:
        return f"Increase passwordless adoption from {adoption_rate}% to 50%+ for improved security and user experience"
    
    return ""
