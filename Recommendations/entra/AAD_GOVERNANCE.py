"""
Microsoft Entra ID Governance - Enhanced with PIM and Access Reviews Analysis
Provides license check + PIM configuration + Access Reviews governance for Copilot administration.
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Generate Entra ID Governance recommendations with PIM and Access Reviews analysis.
    
    Returns multiple observations:
    1. License check (with upgrade path for lower SKUs)
    2. PIM configuration analysis (if entra_insights available):
       - Permanent admin roles: High priority - Enable JIT access
       - Eligible assignments configured: Success
    3. Access Reviews configuration (admin roles and Copilot licenses)
    
    Args:
        sku_name: SKU name where feature is found
        status: Provisioning status
        client: Graph client (unused, for compatibility)
        entra_insights: Pre-computed identity metrics with pim_metrics and access_review_metrics
    """
    feature_name = "Microsoft Entra ID Governance"
    friendly_sku = get_friendly_sku_name(sku_name)
    observations = []
    
    # ========================================
    # OBSERVATION 1: License Check
    # ========================================
    if status == "Success":
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling automated access governance for Copilot administration",
            recommendation="",
            link_text="Govern Copilot Access Rights",
            link_url="https://learn.microsoft.com/entra/id-governance/",
            status=status
        ))
    else:
        # License not available - drive upgrade for Copilot governance
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku} - upgrade required for Copilot access governance and PIM",
            recommendation=f"Upgrade to Microsoft Entra ID Governance (or E5) to enable critical access governance for Copilot deployment: 1) Privileged Identity Management (PIM) for just-in-time admin access - prevents standing admin privileges that can override Copilot security controls, 2) Access Reviews to periodically certify admin role assignments and Copilot license assignments - ensures only authorized users maintain Copilot access, 3) Lifecycle Workflows to automatically revoke Copilot access when employees leave, 4) Entitlement Management to automate Copilot license requests and approvals based on business justification. Without governance, permanent admin roles can bypass Copilot security, dormant accounts retain AI access, and you lack visibility into who should have Copilot privileges. Essential for compliance (SOC 2, ISO 27001) and preventing unauthorized AI usage.",
            link_text="Identity Governance Overview",
            link_url="https://learn.microsoft.com/entra/id-governance/identity-governance-overview",
            priority="High",
            status=status
        ))
    
    # ========================================
    # OBSERVATION 2: PIM Configuration
    # ========================================
    if entra_insights and status == "Success":
        pim_metrics = entra_insights.get('pim_metrics', {})
        permanent_admin_roles = pim_metrics.get('permanent_admin_roles', 0)
        eligible_assignments = pim_metrics.get('eligible_assignments', 0)
        
        # Permanent admin roles detected - security risk
        if permanent_admin_roles > 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"{permanent_admin_roles} permanent admin role assignment(s) detected - standing privileges can override Copilot security controls",
                recommendation=f"Convert {permanent_admin_roles} permanent admin role(s) to time-bound eligible assignments using Privileged Identity Management (PIM). Permanent admins have standing privileges to: 1) Bypass Copilot security policies and DLP rules, 2) Access all Copilot prompts and responses in audit logs, 3) Modify sensitivity labels and data governance, 4) Override Conditional Access policies blocking Copilot. Implement PIM to require just-in-time activation with MFA and business justification. Admin roles to convert: Global Administrator, SharePoint Administrator, Teams Administrator, Compliance Administrator. This limits the blast radius if admin accounts are compromised and ensures audit trail of privileged actions affecting Copilot.",
                link_text="Configure PIM for Admins",
                link_url="https://learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-configure",
                priority="High",
                status=status
            ))
        
        # PIM configured with eligible assignments
        elif eligible_assignments > 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"Privileged Identity Management configured with {eligible_assignments} eligible admin role assignment(s), enforcing just-in-time access",
                recommendation="",
                link_text="PIM Best Practices",
                link_url="https://learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-configure",
                status=status
            ))
    
    # ========================================
    # OBSERVATION 3: Access Reviews
    # ========================================
    if entra_insights and status == "Success":
        review_metrics = entra_insights.get('access_review_metrics', {})
        total_reviews = review_metrics.get('total_reviews', 0)
        active_reviews = review_metrics.get('active_reviews', 0)
        admin_role_reviews = review_metrics.get('admin_role_reviews', 0)
        
        # No access reviews configured
        if total_reviews == 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="No access reviews configured for admin roles or Copilot license assignments",
                recommendation="Implement quarterly access reviews to certify: 1) Admin role assignments - ensure only authorized personnel maintain privileges that can override Copilot controls, 2) Copilot license assignments - verify users still require AI assistant access and remove licenses from inactive/transferred employees, 3) Guest user access - review external users who can access content Copilot searches. Create recurring reviews in Entra ID Governance targeting: 'Directory Roles' for admin certification, user groups with Copilot licenses for usage validation. Set reviewers as department managers or license owners. Prevents privilege creep and reduces security/licensing costs.",
                link_text="Configure Access Reviews",
                link_url="https://learn.microsoft.com/entra/id-governance/access-reviews-overview",
                priority="Medium",
                status=status
            ))
        
        # Access reviews configured
        else:
            review_details = f"{total_reviews} access review definition(s) configured"
            if active_reviews > 0:
                review_details += f", {active_reviews} currently active"
            if admin_role_reviews > 0:
                review_details += f", {admin_role_reviews} reviewing admin roles"
            
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"Access governance active: {review_details}",
                recommendation="",
                link_text="Access Reviews Best Practices",
                link_url="https://learn.microsoft.com/entra/id-governance/access-reviews-overview",
                status=status
            ))
    
    # ========================================
    # OBSERVATION 4: Application Consent Settings
    # ========================================
    if entra_insights and status == "Success":
        print(f"[DEBUG GOV] App consent check - entra_insights available: {entra_insights is not None}")
        consent_metrics = entra_insights.get('consent_summary', {})
        print(f"[DEBUG GOV] consent_summary extracted: {consent_metrics}")
        user_consent_allowed = consent_metrics.get('user_consent_allowed', False)
        admin_consent_required = consent_metrics.get('admin_consent_required', False)
        print(f"[DEBUG GOV] User consent: {user_consent_allowed}, Admin required: {admin_consent_required}")
        
        # User consent enabled - security risk
        if user_consent_allowed and not admin_consent_required:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="User consent enabled for applications, allowing users to grant apps access to Copilot-generated content and M365 data without admin review",
                recommendation="Disable user consent and require admin approval for all application permissions to prevent unauthorized apps from accessing Copilot data. With user consent enabled, employees can: 1) Grant malicious apps access to their emails, files, Teams messages - all searchable by Copilot, 2) Approve apps that extract Copilot prompts/responses via Graph API, 3) Inadvertently share organizational knowledge with third-party services, 4) Create compliance violations (GDPR, HIPAA) through unvetted integrations. Configure consent settings to 'Do not allow user consent' and enable admin consent workflow so IT can review app permissions before granting access. This ensures only vetted applications interact with Copilot-accessible data.",
                link_text="Configure User Consent",
                link_url="https://learn.microsoft.com/entra/identity/enterprise-apps/configure-user-consent",
                priority="High",
                status=status
            ))
        elif admin_consent_required:
            # Success: Admin consent required
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="Admin consent required for applications, protecting Copilot data from unauthorized app access",
                recommendation="",
                link_text="Admin Consent Workflow",
                link_url="https://learn.microsoft.com/entra/identity/enterprise-apps/configure-admin-consent-workflow",
                status=status
            ))
    
    # ========================================
    # OBSERVATION 5: Risky Application Permissions
    # ========================================
    if entra_insights and status == "Success":
        consent_metrics = entra_insights.get('consent_summary', {})
        high_privilege_apps = consent_metrics.get('high_privilege_apps', 0)
        unverified_publishers = consent_metrics.get('unverified_publishers', 0)
        apps_with_graph = consent_metrics.get('apps_with_graph_access', 0)
        apps_with_mail = consent_metrics.get('apps_with_mail_access', 0)
        apps_with_files = consent_metrics.get('apps_with_files_access', 0)
        print(f"[DEBUG GOV] Risky apps - High privilege: {high_privilege_apps}, Unverified: {unverified_publishers}, Graph: {apps_with_graph}, Mail: {apps_with_mail}, Files: {apps_with_files}")
        
        # High-privilege or unverified apps detected
        if high_privilege_apps > 0 or unverified_publishers > 0:
            risk_details = []
            if high_privilege_apps > 0:
                risk_details.append(f"{high_privilege_apps} with high-privilege permissions")
            if unverified_publishers > 0:
                risk_details.append(f"{unverified_publishers} from unverified publishers")
            if apps_with_graph > 0:
                risk_details.append(f"{apps_with_graph} accessing Graph API (Copilot data)")
            
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"Risky applications detected: {', '.join(risk_details)} - potential unauthorized access to Copilot-generated content",
                recommendation=f"Audit and restrict {high_privilege_apps + unverified_publishers} risky application(s) with access to M365 data and Copilot content. High-privilege apps can: 1) Read all emails and extract Copilot summaries ({apps_with_mail} apps with Mail.Read), 2) Access all SharePoint files and Copilot-indexed documents ({apps_with_files} apps with Files.Read), 3) Query Graph API to retrieve Copilot prompts and responses ({apps_with_graph} apps with Graph access), 4) Operate as unverified publishers without Microsoft validation ({unverified_publishers} apps). Review each app's permissions in Azure AD > Enterprise Applications > Permissions, revoke excessive permissions, and remove unnecessary apps. Implement app governance policies to detect risky permission grants automatically. Critical for preventing data exfiltration through third-party integrations.",
                link_text="App Governance",
                link_url="https://learn.microsoft.com/defender-cloud-apps/app-governance-manage-app-governance",
                priority="High",
                status=status
            ))
        else:
            # Success: No risky apps
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="No high-risk applications detected, app permissions appropriately scoped for Copilot data protection",
                recommendation="",
                link_text="App Permission Best Practices",
                link_url="https://learn.microsoft.com/entra/identity/enterprise-apps/manage-application-permissions",
                status=status
            ))
    
    return observations
