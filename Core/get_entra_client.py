"""
Microsoft Entra Client
Provides authenticated access to Microsoft Entra ID (formerly Azure AD) APIs.
Fetches and caches: Conditional Access policies, MFA registration, Identity Protection,
PIM, Access Reviews, Device Compliance, B2B settings, and Application Consent data.
Used for enhanced Entra observations focused on Copilot adoption.
"""
import asyncio
import httpx
from azure.core.exceptions import HttpResponseError
from .spinner import get_timestamp, _stdout_lock
from datetime import datetime, timedelta

def _get_attr(obj, attr_name, default=''):
    """Helper to safely get attribute from SDK object with snake_case conversion"""
    if obj is None:
        return default
    # Try direct attribute access first
    value = getattr(obj, attr_name, None)
    if value is not None:
        return value
    # Try snake_case version (e.g., grantControls -> grant_controls)
    import re
    snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', attr_name).lower()
    value = getattr(obj, snake_case, None)
    return value if value is not None else default

async def _get_graph_http_client():
    """Get HTTP client for Microsoft Graph API with bearer token"""
    from .get_graph_client import get_shared_credential
    
    credential = get_shared_credential()
    token = credential.get_token('https://graph.microsoft.com/.default')
    
    return httpx.AsyncClient(
        base_url='https://graph.microsoft.com',
        headers={
            "Authorization": f"Bearer {token.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        timeout=30.0
    )

async def get_entra_client(graph_client, tenant_id=None):
    """
    Get authenticated client for Microsoft Entra ID (Azure AD) APIs.
    Fetches comprehensive identity, security, and compliance data.
    
    Args:
        graph_client: Existing Microsoft Graph SDK client
        tenant_id: Azure tenant ID (optional)
    
    Returns:
        EntraClient object with cached Entra data and pre-computed summaries,
        or minimal client if permissions are insufficient (graceful degradation)
    """
    
    class EntraClient:
        def __init__(self):
            self.available = False
            
            # Conditional Access
            self.ca_policies = []
            self.ca_summary = {
                'total': 0,
                'require_mfa': 0,
                'require_compliant_device': 0,
                'require_managed_device': 0,
                'target_m365_apps': 0,
                'target_all_apps': 0,
                'block_legacy_auth': 0,
                'location_based': 0,
                'user_risk_based': 0,
                'signin_risk_based': 0,
                'enabled': 0,
                'disabled': 0,
                'report_only': 0
            }
            
            # MFA & Authentication Methods
            self.auth_methods_registration = []
            self.auth_summary = {
                'total_users': 0,
                'mfa_registered': 0,
                'mfa_capable': 0,
                'passwordless_enabled': 0,
                'mfa_registration_rate': 0,
                'passwordless_adoption_rate': 0,
                'methods': {
                    'microsoftAuthenticator': 0,
                    'fido2': 0,
                    'windowsHello': 0,
                    'phone': 0,
                    'email': 0,
                    'softwareOath': 0,
                    'temporaryAccessPass': 0
                }
            }
            
            # Identity Protection
            self.risky_users = []
            self.risk_detections = []
            self.risk_summary = {
                'risky_users_total': 0,
                'risky_users_high': 0,
                'risky_users_medium': 0,
                'risky_users_low': 0,
                'confirmed_compromised': 0,
                'at_risk': 0,
                'remediated': 0,
                'dismissed': 0,
                'risk_detections_total': 0,
                'risk_detections_high': 0,
                'user_risk_policy_exists': False,
                'signin_risk_policy_exists': False
            }
            
            # Privileged Identity Management (PIM)
            self.role_assignments = []
            self.role_eligibility_schedules = []
            self.role_assignment_schedules = []
            self.pim_summary = {
                'total_active_assignments': 0,
                'total_eligible_assignments': 0,
                'total_time_bound_assignments': 0,
                'permanent_assignments': 0,
                'permanent_global_admins': 0,
                'permanent_privileged_roles': 0,
                'eligible_assignments': 0,
                'pim_enabled_roles': 0,
                'roles_with_only_permanent': 0
            }
            
            # Access Reviews
            self.access_reviews = []
            self.access_review_summary = {
                'total_definitions': 0,
                'active_reviews': 0,
                'group_membership_reviews': 0,
                'role_assignment_reviews': 0,
                'application_assignment_reviews': 0,
                'guest_user_reviews': 0,
                'recurring_reviews': 0,
                'one_time_reviews': 0
            }
            
            # Device Management & Compliance
            self.managed_devices = []
            self.compliance_policies = []
            self.device_summary = {
                'total_managed': 0,
                'compliant': 0,
                'non_compliant': 0,
                'in_grace_period': 0,
                'not_applicable': 0,
                'error': 0,
                'corporate_owned': 0,
                'personal_byod': 0,
                'windows': 0,
                'ios': 0,
                'android': 0,
                'macos': 0,
                'compliance_policies_total': 0,
                'ca_requires_compliance': False
            }
            
            # Group-Based Licensing
            self.groups_with_licenses = []
            self.group_licensing_summary = {
                'total_groups_with_licenses': 0,
                'groups_with_errors': 0,
                'total_license_errors': 0,
                'copilot_license_groups': 0,
                'dynamic_groups': 0,
                'security_groups': 0,
                'distribution_groups': 0
            }
            
            # External Collaboration (B2B)
            self.guest_users = []
            self.cross_tenant_access_policy = {}
            self.b2b_summary = {
                'total_guests': 0,
                'guests_with_licenses': 0,
                'guest_invite_restrictions': 'Unknown',
                'cross_tenant_access_configured': False,
                'default_settings': {},
                'partner_configurations': 0
            }
            
            # Application Consent & Permissions
            self.service_principals = []
            self.oauth_permission_grants = []
            self.permission_grant_policies = []
            self.consent_summary = {
                'total_apps': 0,
                'apps_with_delegated_permissions': 0,
                'apps_with_application_permissions': 0,
                'user_consent_allowed': False,
                'admin_consent_required': False,
                'high_privilege_apps': 0,
                'apps_with_graph_access': 0,
                'apps_with_mail_access': 0,
                'apps_with_files_access': 0,
                'unverified_publishers': 0
            }
            
            # Sign-in Logs (Sample - last 7 days)
            self.signin_logs = []
            self.signin_summary = {
                'total_signins_sampled': 0,
                'legacy_auth_attempts': 0,
                'mfa_required': 0,
                'mfa_success': 0,
                'mfa_failure': 0,
                'ca_success': 0,
                'ca_failure': 0,
                'failed_signins': 0,
                'risky_signins': 0
            }
            
            # Global Secure Access (Entra Internet Access)
            self.network_filtering_policies = []
            self.network_forwarding_profiles = []
            self.network_access_summary = {
                'status': 'Success',
                'error': None,
                'enabled': False,
                'total_filtering_policies': 0,
                'total_forwarding_profiles': 0,
                'web_filtering_enabled': False,
                'traffic_forwarding_enabled': False,
                'fqdn_rules_count': 0,
                'web_category_rules_count': 0,
                'm365_traffic_forwarding': False,
                'internet_traffic_forwarding': False
            }
            
            # Global Secure Access (Entra Private Access)
            self.private_access_connectors = []
            self.private_access_apps = []
            self.private_access_summary = {
                'status': 'Success',
                'error': None,
                'enabled': False,
                'total_connectors': 0,
                'active_connectors': 0,
                'total_apps': 0,
                'apps_with_quick_access': 0,
                'apps_with_per_app_access': 0
            }
            
            # Policy Read (Auth Policy, Consent Policies)
            self.authorization_policy = {}
            self.auth_policy_summary = {
                'guest_invite_setting': 'Unknown',
                'default_user_role_permissions': {},
                'allow_users_to_register_apps': False
            }
    
    client_obj = EntraClient()
    
    import sys
    from .spinner import _stdout_lock, get_timestamp
    
    # Show initial progress bar
    with _stdout_lock:
        sys.stdout.write(f'\r[{get_timestamp()}]   Entra Data Gathering    [░░░░░░░░░░░░░░░░░░░░]   0%')
        sys.stdout.flush()
    
    # Create progress update task
    async def update_progress():
        for i in range(1, 101):
            await asyncio.sleep(0.2)  # ~20 seconds total
            progress = i / 100
            filled = int(20 * progress)
            bar = '█' * filled + '░' * (20 - filled)
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   Entra Data Gathering    [{bar}] {i:3d}%')
                sys.stdout.flush()
    
    progress_task = asyncio.create_task(update_progress())
    
    try:
        # Define all API calls using proper SDK object model
        # Group by dependencies - some can run together, others need results first
        
        # Phase 1: Core data (no dependencies)
        phase1_tasks = {}
        
        try:
            # Conditional Access policies
            phase1_tasks['ca_policies'] = graph_client.identity.conditional_access.policies.get()
        except Exception:
            pass
        
        try:
            # Authentication methods user registration details
            phase1_tasks['auth_methods'] = graph_client.reports.authentication_methods.user_registration_details.get()
        except Exception:
            pass
        
        try:
            # Risky users from Identity Protection
            phase1_tasks['risky_users'] = graph_client.identity_protection.risky_users.get()
        except Exception:
            pass
        
        try:
            # Risk detections from Identity Protection
            phase1_tasks['risk_detections'] = graph_client.identity_protection.risk_detections.get()
        except Exception:
            pass
        
        try:
            # Role assignments (PIM)
            phase1_tasks['role_assignments'] = graph_client.role_management.directory.role_assignments.get()
        except Exception:
            pass
        
        try:
            # Role eligibility schedules (PIM)
            phase1_tasks['role_eligibility_schedules'] = graph_client.role_management.directory.role_eligibility_schedules.get()
        except Exception:
            pass
        
        try:
            # Role assignment schedules (PIM)
            phase1_tasks['role_assignment_schedules'] = graph_client.role_management.directory.role_assignment_schedules.get()
        except Exception:
            pass
        
        try:
            # Access reviews
            phase1_tasks['access_reviews'] = graph_client.identity_governance.access_reviews.definitions.get()
        except Exception:
            pass
        
        try:
            # Managed devices (Intune)
            phase1_tasks['managed_devices'] = graph_client.device_management.managed_devices.get()
        except Exception:
            pass
        
        try:
            # Device compliance policies (Intune)
            phase1_tasks['compliance_policies'] = graph_client.device_management.device_compliance_policies.get()
        except Exception:
            pass
        
        try:
            # Groups with licenses
            from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
            query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
                filter="assignedLicenses/$count ne 0",
                select=["id", "displayName", "groupTypes", "assignedLicenses", "licenseProcessingState"],
                top=999
            )
            request_config = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(query_parameters=query_params)
            phase1_tasks['groups'] = graph_client.groups.get(request_configuration=request_config)
        except Exception:
            pass
        
        try:
            # Guest users
            from msgraph.generated.users.users_request_builder import UsersRequestBuilder
            query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                filter="userType eq 'Guest'",
                select=["id", "displayName", "userPrincipalName", "createdDateTime", "assignedLicenses"],
                top=999
            )
            request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(query_parameters=query_params)
            phase1_tasks['guests'] = graph_client.users.get(request_configuration=request_config)
        except Exception:
            pass
        
        try:
            # Cross-tenant access policy (B2B)
            phase1_tasks['cross_tenant_policy'] = graph_client.policies.cross_tenant_access_policy.get()
        except Exception:
            pass
        
        try:
            # Service principals
            from msgraph.generated.service_principals.service_principals_request_builder import ServicePrincipalsRequestBuilder
            query_params = ServicePrincipalsRequestBuilder.ServicePrincipalsRequestBuilderGetQueryParameters(
                select=["id", "appId", "displayName", "publisherName", "appRoles", "oauth2PermissionScopes"],
                top=500
            )
            request_config = ServicePrincipalsRequestBuilder.ServicePrincipalsRequestBuilderGetRequestConfiguration(query_parameters=query_params)
            phase1_tasks['service_principals'] = graph_client.service_principals.get(request_configuration=request_config)
        except Exception:
            pass
        
        try:
            # OAuth permission grants
            phase1_tasks['oauth_grants'] = graph_client.oauth2_permission_grants.get()
        except Exception:
            pass
        
        try:
            # Permission grant policies (consent policies)
            phase1_tasks['consent_policies'] = graph_client.policies.permission_grant_policies.get()
        except Exception:
            pass
        
        try:
            # Authorization policy
            phase1_tasks['authorization_policy'] = graph_client.policies.authorization_policy.get()
        except Exception:
            pass
        
        try:
            # Sign-in logs: Last 7 days (legacy auth detection)
            from msgraph.generated.audit_logs.sign_ins.sign_ins_request_builder import SignInsRequestBuilder
            seven_days_ago = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
            query_params = SignInsRequestBuilder.SignInsRequestBuilderGetQueryParameters(
                filter=f"createdDateTime ge {seven_days_ago}",
                top=500
            )
            request_config = SignInsRequestBuilder.SignInsRequestBuilderGetRequestConfiguration(query_parameters=query_params)
            phase1_tasks['signin_logs'] = graph_client.audit_logs.sign_ins.get(request_configuration=request_config)
        except Exception:
            pass
        
        # Execute all phase 1 tasks in parallel
        phase1_results = {}
        if phase1_tasks:
            results = await asyncio.gather(*phase1_tasks.values(), return_exceptions=True)
            phase1_results = dict(zip(phase1_tasks.keys(), results))
        
        # Process Conditional Access Policies
        ca_response = phase1_results.get('ca_policies')
        if ca_response and not isinstance(ca_response, Exception):
            try:
                # SDK returns collection response objects with .value property
                policies = ca_response.value if hasattr(ca_response, 'value') else []
                client_obj.ca_policies = policies
                
                # Analyze policies
                for policy in policies:
                    client_obj.ca_summary['total'] += 1
                    
                    state = (_get_attr(policy, 'state') or '').lower()
                    if state == 'enabled':
                        client_obj.ca_summary['enabled'] += 1
                    elif state == 'disabled':
                        client_obj.ca_summary['disabled'] += 1
                    elif state == 'enabledForReportingButNotEnforced' or state == 'enabled_for_reporting_but_not_enforced':
                        client_obj.ca_summary['report_only'] += 1
                    
                    # Check grant controls
                    grant_controls = _get_attr(policy, 'grantControls')
                    if grant_controls:
                        built_in_controls = _get_attr(grant_controls, 'builtInControls', []) or []
                        
                        if 'mfa' in built_in_controls:
                            client_obj.ca_summary['require_mfa'] += 1
                        if 'compliantDevice' in built_in_controls:
                            client_obj.ca_summary['require_compliant_device'] += 1
                        if 'domainJoinedDevice' in built_in_controls or 'approvedApplication' in built_in_controls:
                            client_obj.ca_summary['require_managed_device'] += 1
                    
                    # Check conditions
                    conditions = _get_attr(policy, 'conditions')
                    if conditions:
                        # Applications targeted
                        apps = _get_attr(conditions, 'applications')
                        if apps:
                            include_apps = _get_attr(apps, 'includeApplications', []) or []
                            if 'All' in include_apps:
                                client_obj.ca_summary['target_all_apps'] += 1
                            if '00000003-0000-0ff1-ce00-000000000000' in include_apps:  # Office 365
                                client_obj.ca_summary['target_m365_apps'] += 1
                        
                        # Client app types (legacy auth blocking)
                        client_app_types = _get_attr(conditions, 'clientAppTypes', []) or []
                        if client_app_types and 'exchangeActiveSync' not in client_app_types and 'other' not in client_app_types:
                            client_obj.ca_summary['block_legacy_auth'] += 1
                        
                        # Risk-based policies
                        user_risk_levels = _get_attr(conditions, 'userRiskLevels', []) or []
                        signin_risk_levels = _get_attr(conditions, 'signInRiskLevels', []) or []
                        if user_risk_levels:
                            client_obj.ca_summary['user_risk_based'] += 1
                            client_obj.risk_summary['user_risk_policy_exists'] = True
                        if signin_risk_levels:
                            client_obj.ca_summary['signin_risk_based'] += 1
                            client_obj.risk_summary['signin_risk_policy_exists'] = True
                    
                        # Location-based
                        locations = _get_attr(conditions, 'locations')
                        if locations:
                            client_obj.ca_summary['location_based'] += 1
                
                # Check if CA requires compliance
                if client_obj.ca_summary['require_compliant_device'] > 0:
                    client_obj.device_summary['ca_requires_compliance'] = True
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: CA policies parse error: {e}")
        
        # Process Authentication Methods Registration
        auth_response = phase1_results.get('auth_methods')
        if auth_response and not isinstance(auth_response, Exception):
            try:
                # SDK returns collection response objects with .value property
                registrations = auth_response.value if hasattr(auth_response, 'value') else []
                client_obj.auth_methods_registration = registrations
                
                client_obj.auth_summary['total_users'] = len(registrations)
                
                for user_reg in registrations:
                    # SDK objects use attributes, not .get()
                    is_mfa_registered = getattr(user_reg, 'is_mfa_registered', False)
                    is_mfa_capable = getattr(user_reg, 'is_mfa_capable', False)
                    
                    if is_mfa_registered:
                        client_obj.auth_summary['mfa_registered'] += 1
                    if is_mfa_capable:
                        client_obj.auth_summary['mfa_capable'] += 1
                    
                    methods = getattr(user_reg, 'methods_registered', []) or []
                    
                    # Check passwordless methods
                    passwordless_methods = ['microsoftAuthenticator', 'fido2', 'windowsHello']
                    if any(m in methods for m in passwordless_methods):
                        client_obj.auth_summary['passwordless_enabled'] += 1
                    
                    # Count by method type
                    for method in methods:
                        if method in client_obj.auth_summary['methods']:
                            client_obj.auth_summary['methods'][method] += 1
                
                # Calculate rates
                total = client_obj.auth_summary['total_users']
                if total > 0:
                    client_obj.auth_summary['mfa_registration_rate'] = int((client_obj.auth_summary['mfa_registered'] / total) * 100)
                    client_obj.auth_summary['passwordless_adoption_rate'] = int((client_obj.auth_summary['passwordless_enabled'] / total) * 100)
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Auth methods parse error: {e}")
        
        # Process Risky Users
        risky_response = phase1_results.get('risky_users')
        if risky_response and not isinstance(risky_response, Exception):
            try:
                risky_data = risky_response.json() if hasattr(risky_response, 'json') else risky_response
                risky_users = risky_data.get('value', []) if isinstance(risky_data, dict) else []
                client_obj.risky_users = risky_users
                
                client_obj.risk_summary['risky_users_total'] = len(risky_users)
                
                for user in risky_users:
                    risk_level = user.get('riskLevel', '').lower()
                    risk_state = user.get('riskState', '').lower()
                    
                    if risk_level == 'high':
                        client_obj.risk_summary['risky_users_high'] += 1
                    elif risk_level == 'medium':
                        client_obj.risk_summary['risky_users_medium'] += 1
                    elif risk_level == 'low':
                        client_obj.risk_summary['risky_users_low'] += 1
                    
                    if risk_state == 'confirmedcompromised':
                        client_obj.risk_summary['confirmed_compromised'] += 1
                    elif risk_state == 'atrisk':
                        client_obj.risk_summary['at_risk'] += 1
                    elif risk_state == 'remediated':
                        client_obj.risk_summary['remediated'] += 1
                    elif risk_state == 'dismissed':
                        client_obj.risk_summary['dismissed'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Risky users parse error: {e}")
        
        # Process Risk Detections
        risk_det_response = phase1_results.get('risk_detections')
        if risk_det_response and not isinstance(risk_det_response, Exception):
            try:
                # SDK returns collection response objects with .value property
                detections = risk_det_response.value if hasattr(risk_det_response, 'value') else []
                client_obj.risk_detections = detections
                
                client_obj.risk_summary['risk_detections_total'] = len(detections)
                
                for detection in detections:
                    risk_level = (_get_attr(detection, 'riskLevel') or '').lower()
                    if risk_level == 'high':
                        client_obj.risk_summary['risk_detections_high'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Risk detections parse error: {e}")
        
        # Process Role Assignments (PIM - Active/Permanent)
        role_assign_response = phase1_results.get('role_assignments')
        if role_assign_response and not isinstance(role_assign_response, Exception):
            try:
                role_data = role_assign_response.json() if hasattr(role_assign_response, 'json') else role_assign_response
                assignments = role_data.get('value', []) if isinstance(role_data, dict) else []
                client_obj.role_assignments = assignments
                
                client_obj.pim_summary['total_active_assignments'] = len(assignments)
                
                # Global Admin role template ID
                global_admin_role = '62e90394-69f5-4237-9190-012177145e10'
                
                for assignment in assignments:
                    role_def_id = assignment.get('roleDefinitionId', '')
                    
                    # Check if permanent (no end date in assignment schedule)
                    # For now, count all role_assignments as permanent (vs eligible in schedules)
                    client_obj.pim_summary['permanent_assignments'] += 1
                    
                    if global_admin_role in role_def_id:
                        client_obj.pim_summary['permanent_global_admins'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Role assignments parse error: {e}")
        
        # Process Role Eligibility Schedules (PIM - Eligible)
        role_elig_response = phase1_results.get('role_eligibility_schedules')
        if role_elig_response and not isinstance(role_elig_response, Exception):
            try:
                elig_data = role_elig_response.json() if hasattr(role_elig_response, 'json') else role_elig_response
                schedules = elig_data.get('value', []) if isinstance(elig_data, dict) else []
                client_obj.role_eligibility_schedules = schedules
                
                client_obj.pim_summary['total_eligible_assignments'] = len(schedules)
                client_obj.pim_summary['eligible_assignments'] = len(schedules)
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Role eligibility parse error: {e}")
        
        # Process Role Assignment Schedules (PIM - Time-bound active)
        role_sched_response = phase1_results.get('role_assignment_schedules')
        if role_sched_response and not isinstance(role_sched_response, Exception):
            try:
                sched_data = role_sched_response.json() if hasattr(role_sched_response, 'json') else role_sched_response
                schedules = sched_data.get('value', []) if isinstance(sched_data, dict) else []
                client_obj.role_assignment_schedules = schedules
                
                client_obj.pim_summary['total_time_bound_assignments'] = len(schedules)
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Role schedules parse error: {e}")
        
        # Calculate PIM metrics
        if client_obj.pim_summary['total_eligible_assignments'] > 0:
            client_obj.pim_summary['pim_enabled_roles'] = client_obj.pim_summary['total_eligible_assignments']
        
        # Process Access Reviews
        reviews_response = phase1_results.get('access_reviews')
        if reviews_response and not isinstance(reviews_response, Exception):
            try:
                # SDK returns collection response objects with .value property
                reviews = reviews_response.value if hasattr(reviews_response, 'value') else []
                client_obj.access_reviews = reviews
                
                client_obj.access_review_summary['total_definitions'] = len(reviews)
                
                for review in reviews:
                    status = (_get_attr(review, 'status') or '').lower()
                    if status in ['inprogress', 'notstarted']:
                        client_obj.access_review_summary['active_reviews'] += 1
                    
                    # Check scope type
                    scope = _get_attr(review, 'scope')
                    query = (_get_attr(scope, 'query') or '').lower() if scope else ''
                    
                    if 'group' in query or 'groupmember' in query:
                        client_obj.access_review_summary['group_membership_reviews'] += 1
                    if 'roleassignment' in query or 'role' in query:
                        client_obj.access_review_summary['role_assignment_reviews'] += 1
                    if 'guest' in query or 'usertype' in query:
                        client_obj.access_review_summary['guest_user_reviews'] += 1
                    
                    # Check recurrence
                    settings = review.get('settings', {})
                    recurrence = settings.get('recurrence', {})
                    if recurrence and recurrence.get('pattern'):
                        client_obj.access_review_summary['recurring_reviews'] += 1
                    else:
                        client_obj.access_review_summary['one_time_reviews'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Access reviews parse error: {e}")
        
        # Process Managed Devices
        devices_response = phase1_results.get('managed_devices')
        if devices_response and not isinstance(devices_response, Exception):
            try:
                devices_data = devices_response.json() if hasattr(devices_response, 'json') else devices_response
                devices = devices_data.get('value', []) if isinstance(devices_data, dict) else []
                client_obj.managed_devices = devices
                
                client_obj.device_summary['total_managed'] = len(devices)
                
                for device in devices:
                    compliance = device.get('complianceState', '').lower()
                    if compliance == 'compliant':
                        client_obj.device_summary['compliant'] += 1
                    elif compliance == 'noncompliant':
                        client_obj.device_summary['non_compliant'] += 1
                    elif compliance == 'ingraceperiod':
                        client_obj.device_summary['in_grace_period'] += 1
                    elif compliance == 'error':
                        client_obj.device_summary['error'] += 1
                    
                    ownership = device.get('managedDeviceOwnerType', '').lower()
                    if ownership == 'company':
                        client_obj.device_summary['corporate_owned'] += 1
                    elif ownership == 'personal':
                        client_obj.device_summary['personal_byod'] += 1
                    
                    os = device.get('operatingSystem', '').lower()
                    if 'windows' in os:
                        client_obj.device_summary['windows'] += 1
                    elif 'ios' in os:
                        client_obj.device_summary['ios'] += 1
                    elif 'android' in os:
                        client_obj.device_summary['android'] += 1
                    elif 'mac' in os:
                        client_obj.device_summary['macos'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Devices parse error: {e}")
        
        # Process Compliance Policies
        compliance_response = phase1_results.get('compliance_policies')
        if compliance_response and not isinstance(compliance_response, Exception):
            try:
                # SDK returns collection response objects with .value property
                policies = compliance_response.value if hasattr(compliance_response, 'value') else []
                client_obj.compliance_policies = policies
                
                client_obj.device_summary['compliance_policies_total'] = len(policies)
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Compliance policies parse error: {e}")
        
        # Process Groups with Licenses
        groups_response = phase1_results.get('groups')
        if groups_response and not isinstance(groups_response, Exception):
            try:
                # SDK returns collection response objects with .value property
                groups = groups_response.value if hasattr(groups_response, 'value') else []
                client_obj.groups_with_licenses = groups
                
                client_obj.group_licensing_summary['total_groups_with_licenses'] = len(groups)
                
                # Copilot-related SKU part numbers
                copilot_sku_keywords = ['COPILOT', 'M365_COPILOT', 'MICROSOFT_365_COPILOT']
                
                for group in groups:
                    # Check for errors
                    license_state = group.get('licenseProcessingState', {})
                    if license_state and license_state.get('state') == 'ProcessingFailed':
                        client_obj.group_licensing_summary['groups_with_errors'] += 1
                    
                    # Check group type
                    group_types = group.get('groupTypes', [])
                    if 'DynamicMembership' in group_types:
                        client_obj.group_licensing_summary['dynamic_groups'] += 1
                    
                    # Check for Copilot licenses (approximate - would need SKU lookup)
                    display_name = group.get('displayName', '').upper()
                    if any(keyword in display_name for keyword in copilot_sku_keywords):
                        client_obj.group_licensing_summary['copilot_license_groups'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Groups parse error: {e}")
        
        # Process Guest Users
        guests_response = phase1_results.get('guests')
        if guests_response and not isinstance(guests_response, Exception):
            try:
                # SDK returns collection response objects with .value property
                guests = guests_response.value if hasattr(guests_response, 'value') else []
                client_obj.guest_users = guests
                
                client_obj.b2b_summary['total_guests'] = len(guests)
                
                # Count guests with licenses
                for guest in guests:
                    licenses = getattr(guest, 'assigned_licenses', []) or []
                    if licenses and len(licenses) > 0:
                        client_obj.b2b_summary['guests_with_licenses'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Guest users parse error: {e}")
        
        # Process Cross-Tenant Access Policy
        cross_tenant_response = phase1_results.get('cross_tenant_policy')
        if cross_tenant_response and not isinstance(cross_tenant_response, Exception):
            try:
                policy_data = cross_tenant_response.json() if hasattr(cross_tenant_response, 'json') else cross_tenant_response
                client_obj.cross_tenant_access_policy = policy_data if isinstance(policy_data, dict) else {}
                
                client_obj.b2b_summary['cross_tenant_access_configured'] = True
                
                # Get default settings
                default = policy_data.get('default', {}) if isinstance(policy_data, dict) else {}
                client_obj.b2b_summary['default_settings'] = default
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Cross-tenant policy parse error: {e}")
        
        # Process Service Principals
        sp_response = phase1_results.get('service_principals')
        if sp_response and not isinstance(sp_response, Exception):
            try:
                sp_data = sp_response.json() if hasattr(sp_response, 'json') else sp_response
                service_principals = sp_data.get('value', []) if isinstance(sp_data, dict) else []
                client_obj.service_principals = service_principals
                
                client_obj.consent_summary['total_apps'] = len(service_principals)
                
                # Analyze app permissions
                graph_app_id = '00000003-0000-0000-c000-000000000000'
                
                for sp in service_principals:
                    app_roles = sp.get('appRoles', [])
                    oauth_scopes = sp.get('oauth2PermissionScopes', [])
                    publisher = sp.get('publisherName', '')
                    
                    # Check if unverified publisher
                    if not publisher or publisher.lower() == 'unverified':
                        client_obj.consent_summary['unverified_publishers'] += 1
                    
                    # Note: Full permission analysis requires cross-referencing with oauth2PermissionGrants
                    # This is simplified for initial implementation
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Service principals parse error: {e}")
        
        # Process OAuth Permission Grants
        oauth_response = phase1_results.get('oauth_grants')
        if oauth_response and not isinstance(oauth_response, Exception):
            try:
                oauth_data = oauth_response.json() if hasattr(oauth_response, 'json') else oauth_response
                grants = oauth_data.get('value', []) if isinstance(oauth_data, dict) else []
                client_obj.oauth_permission_grants = grants
                
                client_obj.consent_summary['apps_with_delegated_permissions'] = len(grants)
                
                # Analyze for Graph API access, Mail, Files
                graph_resource_id = '00000003-0000-0000-c000-000000000000'
                
                for grant in grants:
                    resource_id = _get_attr(grant, 'resourceId', '')
                    scope = (_get_attr(grant, 'scope') or '').lower()
                    
                    if resource_id == graph_resource_id or 'graph' in scope:
                        client_obj.consent_summary['apps_with_graph_access'] += 1
                    
                    if 'mail' in scope:
                        client_obj.consent_summary['apps_with_mail_access'] += 1
                    if 'files' in scope or 'sharepoint' in scope:
                        client_obj.consent_summary['apps_with_files_access'] += 1
                    
                    # High privilege detection (simplified)
                    high_priv_scopes = ['mail.readwrite', 'files.readwrite', 'directory.readwrite']
                    if any(priv in scope for priv in high_priv_scopes):
                        client_obj.consent_summary['high_privilege_apps'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: OAuth grants parse error: {e}")
        
        # Process Permission Grant Policies
        consent_pol_response = phase1_results.get('consent_policies')
        if consent_pol_response and not isinstance(consent_pol_response, Exception):
            try:
                # SDK returns collection response objects with .value property
                policies = consent_pol_response.value if hasattr(consent_pol_response, 'value') else []
                client_obj.permission_grant_policies = policies
                
                # Check if user consent is allowed
                for policy in policies:
                    policy_id = getattr(policy, 'id', '')
                    if policy_id == 'managePermissionGrantsForSelf.microsoft-user-default-legacy':
                        client_obj.consent_summary['user_consent_allowed'] = True
                    elif policy_id == 'managePermissionGrantsForSelf.microsoft-user-default-low':
                        client_obj.consent_summary['user_consent_allowed'] = True
                
                # If no user consent policy found, admin consent is required
                if not client_obj.consent_summary['user_consent_allowed']:
                    client_obj.consent_summary['admin_consent_required'] = True
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Consent policies parse error: {e}")
        
        # Process Authorization Policy
        auth_pol_response = phase1_results.get('authorization_policy')
        if auth_pol_response and not isinstance(auth_pol_response, Exception):
            try:
                # Authorization policy may return single object or collection
                if hasattr(auth_pol_response, 'value'):
                    policies = auth_pol_response.value or []
                    policy = policies[0] if policies else None
                else:
                    policy = auth_pol_response
                
                if policy:
                    client_obj.authorization_policy = policy
                    
                    # Guest invite settings
                    guest_setting = _get_attr(policy, 'allowInvitesFrom', 'Unknown')
                    client_obj.auth_policy_summary['guest_invite_setting'] = guest_setting
                    client_obj.b2b_summary['guest_invite_restrictions'] = guest_setting
                    
                    # Default user permissions
                    default_perms = _get_attr(policy, 'defaultUserRolePermissions')
                    client_obj.auth_policy_summary['default_user_role_permissions'] = default_perms
                    if default_perms:
                        client_obj.auth_policy_summary['allow_users_to_register_apps'] = _get_attr(default_perms, 'allowedToCreateApps', False)
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Auth policy parse error: {e}")
        
        # Process Sign-in Logs
        signin_response = phase1_results.get('signin_logs')
        if signin_response and not isinstance(signin_response, Exception):
            try:
                signin_data = signin_response.json() if hasattr(signin_response, 'json') else signin_response
                signins = signin_data.get('value', []) if isinstance(signin_data, dict) else []
                client_obj.signin_logs = signins
                
                client_obj.signin_summary['total_signins_sampled'] = len(signins)
                
                for signin in signins:
                    client_app = signin.get('clientAppUsed', '').lower()
                    status = signin.get('status', {})
                    error_code = status.get('errorCode', 0)
                    
                    # Legacy auth detection
                    legacy_apps = ['pop', 'imap', 'smtp', 'activesync', 'other clients', 'exchange web services']
                    if any(app in client_app for app in legacy_apps):
                        client_obj.signin_summary['legacy_auth_attempts'] += 1
                    
                    # MFA
                    auth_details = signin.get('authenticationDetails', [])
                    if auth_details:
                        for detail in auth_details:
                            if detail.get('authenticationMethod') == 'MFA':
                                client_obj.signin_summary['mfa_required'] += 1
                                if detail.get('succeeded'):
                                    client_obj.signin_summary['mfa_success'] += 1
                                else:
                                    client_obj.signin_summary['mfa_failure'] += 1
                    
                    # CA status
                    ca_status = signin.get('conditionalAccessStatus', '').lower()
                    if ca_status == 'success':
                        client_obj.signin_summary['ca_success'] += 1
                    elif ca_status == 'failure':
                        client_obj.signin_summary['ca_failure'] += 1
                    
                    # Failed sign-ins
                    if error_code != 0:
                        client_obj.signin_summary['failed_signins'] += 1
                    
                    # Risky sign-ins
                    risk_level = signin.get('riskLevelDuringSignIn', '').lower()
                    if risk_level in ['high', 'medium']:
                        client_obj.signin_summary['risky_signins'] += 1
                
            except Exception as e:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Sign-in logs parse error: {e}")
        
        # ====================================================================
        # GLOBAL SECURE ACCESS (Entra Internet Access) - NetworkAccess API (Beta)
        # ====================================================================
        try:
            # Get HTTP client for direct beta API access
            http_client = await _get_graph_http_client()
            
            try:
                # Filtering Policies (Web Content Filtering)
                filtering_response = await http_client.get('/beta/networkAccess/filteringPolicies')
                filtering_response.raise_for_status()
                filtering_data = filtering_response.json()
                
                if filtering_data and filtering_data.get('value'):
                    policies = filtering_data['value']
                    client_obj.network_filtering_policies = policies
                    client_obj.network_access_summary['total_filtering_policies'] = len(policies)
                    client_obj.network_access_summary['enabled'] = True
                    
                    # Count FQDN and web category rules
                    for policy in policies:
                        policy_rules = policy.get('policyRules', [])
                        if policy_rules:
                            for rule in policy_rules:
                                destinations = rule.get('destinations', [])
                                if destinations:
                                    for dest in destinations:
                                        dest_type = dest.get('@odata.type', '').lower()
                                        if 'fqdn' in dest_type:
                                            client_obj.network_access_summary['fqdn_rules_count'] += 1
                                        elif 'webcategory' in dest_type:
                                            client_obj.network_access_summary['web_category_rules_count'] += 1
                    
                    # Mark web filtering as enabled (policies exist)
                    client_obj.network_access_summary['web_filtering_enabled'] = True
                
                # Forwarding Profiles (Traffic Forwarding Configuration)
                forwarding_response = await http_client.get('/beta/networkAccess/forwardingProfiles')
                forwarding_response.raise_for_status()
                forwarding_data = forwarding_response.json()
                
                if forwarding_data and forwarding_data.get('value'):
                    profiles = forwarding_data['value']
                    client_obj.network_forwarding_profiles = profiles
                    client_obj.network_access_summary['total_forwarding_profiles'] = len(profiles)
                    client_obj.network_access_summary['enabled'] = True
                    
                    # Check if M365 or internet traffic forwarding is configured
                    for profile in profiles:
                        profile_name = profile.get('name', '').lower()
                        profile_state = profile.get('state', '').lower()
                        
                        if profile_state == 'enabled':
                            if 'microsoft365' in profile_name or 'm365' in profile_name:
                                client_obj.network_access_summary['m365_traffic_forwarding'] = True
                            elif 'internet' in profile_name:
                                client_obj.network_access_summary['internet_traffic_forwarding'] = True
                            
                            client_obj.network_access_summary['traffic_forwarding_enabled'] = True
            
            finally:
                # Always close the HTTP client
                await http_client.aclose()
            
            # ====================================================================
            # GLOBAL SECURE ACCESS - PRIVATE ACCESS (Entra Private Access)
            # ====================================================================
            # Get HTTP client for direct beta API access (reuse connection pattern)
            http_client = await _get_graph_http_client()
            
            try:
                # Remote Network Connectors
                connectors_response = await http_client.get('/beta/networkAccess/connectivity/remoteNetworks')
                connectors_response.raise_for_status()
                connectors_data = connectors_response.json()
                
                if connectors_data and connectors_data.get('value'):
                    connectors = connectors_data['value']
                    client_obj.private_access_connectors = connectors
                    client_obj.private_access_summary['total_connectors'] = len(connectors)
                    client_obj.private_access_summary['enabled'] = True
                    
                    # Count active connectors
                    active_count = sum(1 for c in connectors if c.get('connectivityState') == 'alive')
                    client_obj.private_access_summary['active_connectors'] = active_count
                    
                    with _stdout_lock:
                        print(f"[{get_timestamp()}] ✅  Entra: {len(connectors)} Private Access connector(s) found ({active_count} active)")
                
                # Application Segments (Private Access Apps)
                try:
                    # Note: This endpoint may not be available in all tenants
                    apps_response = await http_client.get('/beta/networkAccess/connectivity/branches')
                    apps_response.raise_for_status()
                    apps_data = apps_response.json()
                    
                    if apps_data and apps_data.get('value'):
                        apps = apps_data['value']
                        client_obj.private_access_apps = apps
                        client_obj.private_access_summary['total_apps'] = len(apps)
                        client_obj.private_access_summary['enabled'] = True
                        
                        with _stdout_lock:
                            print(f"[{get_timestamp()}] ✅  Entra: {len(apps)} Private Access app segment(s) configured")
                except httpx.HTTPStatusError:
                    # App segments endpoint may not be available
                    pass
            
            finally:
                # Always close the HTTP client
                await http_client.aclose()
        
        except httpx.HTTPStatusError as e:
            # HTTP error from beta API
            if e.response.status_code == 403:
                client_obj.network_access_summary['status'] = 'PermissionDenied'
                client_obj.network_access_summary['error'] = 'NetworkAccessPolicy.Read.All permission required'
                client_obj.private_access_summary['status'] = 'PermissionDenied'
                client_obj.private_access_summary['error'] = 'NetworkAccessPolicy.Read.All permission required'
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ℹ️     Entra: Global Secure Access API access denied (requires NetworkAccessPolicy.Read.All permission)")
            elif e.response.status_code == 404:
                client_obj.network_access_summary['status'] = 'NotLicensed'
                client_obj.network_access_summary['error'] = 'Entra Suite license required'
                client_obj.private_access_summary['status'] = 'NotLicensed'
                client_obj.private_access_summary['error'] = 'Entra Suite license required'
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ℹ️     Entra: Global Secure Access not available (requires Entra Suite license)")
            else:
                client_obj.network_access_summary['status'] = 'Error'
                client_obj.network_access_summary['error'] = f'HTTP {e.response.status_code}'
                client_obj.private_access_summary['status'] = 'Error'
                client_obj.private_access_summary['error'] = f'HTTP {e.response.status_code}'
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Entra: Global Secure Access API error - HTTP {e.response.status_code}")
        except Exception as e:
            client_obj.network_access_summary['status'] = 'Error'
            client_obj.network_access_summary['error'] = str(e)
            client_obj.private_access_summary['status'] = 'Error'
            client_obj.private_access_summary['error'] = str(e)
            with _stdout_lock:
                print(f"[{get_timestamp()}] ⚠️  Entra: Global Secure Access data fetch failed - {str(e)}")
        
        # Mark client as available if we got at least some data
        if (client_obj.ca_summary['total'] > 0 or 
            client_obj.auth_summary['total_users'] > 0 or 
            client_obj.risk_summary['risky_users_total'] >= 0 or
            client_obj.device_summary['total_managed'] >= 0):
            client_obj.available = True
        else:
            with _stdout_lock:
                print(f"[{get_timestamp()}] ⚠️  Entra: Limited data available (check permissions)")
        
        # Complete progress bar
        progress_task.cancel()
        with _stdout_lock:
            sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Entra Data Gathering    [████████████████████] 100%\n')
            sys.stdout.flush()
        
        return client_obj
        
    except HttpResponseError as e:
        progress_task.cancel()
        with _stdout_lock:
            sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Entra Data Gathering    [████████████████████] 100%\n')
            sys.stdout.flush()
            print(f"[{get_timestamp()}] ⚠️  Entra: HTTP {e.status_code} - {e.message}")
        return client_obj
    
    except Exception as e:
        progress_task.cancel()
        with _stdout_lock:
            sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Entra Data Gathering    [████████████████████] 100%\n')
            sys.stdout.flush()
            print(f"[{get_timestamp()}] ❌    Entra: Unexpected error - {str(e)}")
        return client_obj
