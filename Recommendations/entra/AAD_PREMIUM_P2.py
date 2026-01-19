"""
Microsoft Entra ID P2 - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Microsoft Entra ID P2 provides identity governance and privileged identity management
    critical for managing Copilot admin roles and protecting AI workloads.
    
    When entra_insights is provided, enriches observations with:
    - Privileged Identity Management (PIM) metrics
    - Access Review metrics
    - Identity Protection metrics
    """
    feature_name = "Microsoft Entra ID P2"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    if status == "Success":
        # Base observation for license check
        observation = f"{feature_name} is active in {friendly_sku}, providing identity governance for Copilot administration"
        recommendation_text = ""
        
        # Cache metrics dictionaries (empty if entra_insights not available)
        pim_metrics = {}
        access_review_metrics = {}
        risk_metrics = {}
        
        # Enrich with metrics when entra_insights is available
        if entra_insights and entra_insights.get('available'):
            # Populate metrics dictionaries to avoid redundant lookups
            pim_metrics = entra_insights.get('pim_metrics', {})
            access_review_metrics = entra_insights.get('access_review_metrics', {})
            risk_metrics = entra_insights.get('risk_metrics', {})
            
            metrics = []
            
            # PIM metrics - only show positive findings
            if pim_metrics.get('eligible_admins_count', 0) > 0:
                metrics.append(f"{pim_metrics['eligible_admins_count']} eligible admin(s) configured with PIM")
            
            # Access Review metrics - only show positive findings
            if access_review_metrics.get('total_active_reviews', 0) > 0:
                metrics.append(f"{access_review_metrics['total_active_reviews']} active access review(s)")
            
            if metrics:
                observation += ". " + ", ".join(metrics)
            
            # Generate proactive recommendations based on findings
            recommendation_text = entra_insights.get('pim_recommendation', '')
        
        # Primary license check observation
        recommendations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=observation,
            recommendation=recommendation_text,
            link_text="Identity Governance for Copilot Admins",
            link_url="https://learn.microsoft.com/entra/id-governance/identity-governance-overview",
            status=status
        ))
        
        # Additional observations when entra_insights is available
        if entra_insights and entra_insights.get('available'):
            # Observation 1: PIM configuration status
            permanent_count = pim_metrics.get('permanent_admins_count', 0)
            if permanent_count > 0:
                # Action Required: Permanent admins need PIM
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{permanent_count} admin(s) have permanent elevated privileges, increasing risk for Copilot administrative actions",
                    recommendation=f"Configure Privileged Identity Management (PIM) to require just-in-time activation for admin roles managing Copilot services. This reduces the attack surface for AI workload administration.",
                    link_text="Configure PIM for Copilot Admins",
                    link_url="https://learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-configure",
                    priority="High",
                    status="Action Required"
                ))
            else:
                # Success: No permanent admins (positive finding)
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="No permanent admin roles detected, all administrative access uses just-in-time activation",
                    recommendation="",
                    link_text="PIM Best Practices",
                    link_url="https://learn.microsoft.com/entra/id-governance/privileged-identity-management/pim-configure",
                    status="Success"
                ))
            
            # Observation 2: Access Review configuration status
            active_reviews = access_review_metrics.get('total_active_reviews', 0)
            if active_reviews == 0:
                # Action Required: Missing access reviews
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="No active access reviews configured for user access governance",
                    recommendation="Implement periodic access reviews for users with Copilot licenses and admin roles. Regular reviews ensure only authorized users maintain access to AI assistants and prevent license waste.",
                    link_text="Configure Access Reviews",
                    link_url="https://learn.microsoft.com/entra/id-governance/access-reviews-overview",
                    priority="Medium",
                    status="Action Required"
                ))
            else:
                # Success: Access reviews are configured (positive finding)
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{active_reviews} active access review(s) monitoring user access to Copilot services",
                    recommendation="",
                    link_text="Access Reviews Overview",
                    link_url="https://learn.microsoft.com/entra/id-governance/access-reviews-overview",
                    status="Success"
                ))
            
            # Observation 3: Identity Protection risk status
            high_risk = risk_metrics.get('high_risk_users', 0)
            medium_risk = risk_metrics.get('medium_risk_users', 0)
            if high_risk > 0 or medium_risk > 0:
                # Action Required: Risky users detected
                total_risky = high_risk + medium_risk
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{total_risky} risky user(s) detected ({high_risk} high-risk, {medium_risk} medium-risk) who may have access to Copilot services",
                    recommendation="Review and remediate risky users immediately. Compromised accounts with Copilot access can lead to data exfiltration through AI prompts. Enable risk-based conditional access policies to block risky sign-ins automatically.",
                    link_text="Investigate Risky Users",
                    link_url="https://learn.microsoft.com/entra/id-protection/howto-identity-protection-investigate-risk",
                    priority="High" if high_risk > 0 else "Medium",
                    status="Action Required"
                ))
            else:
                # Success: No risky users (positive finding)
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="No risky users detected, Identity Protection is actively monitoring and protecting accounts",
                    recommendation="",
                    link_text="Identity Protection Overview",
                    link_url="https://learn.microsoft.com/entra/id-protection/overview-identity-protection",
                    status="Success"
                ))
            
            # Observation 4: Guest user (B2B) access to Copilot
            b2b_metrics = entra_insights.get('b2b_summary', {})
            total_guests = b2b_metrics.get('total_guests', 0)
            guests_with_licenses = b2b_metrics.get('guests_with_licenses', 0)
            
            if guests_with_licenses > 0:
                # Action Required: Guests have Copilot access
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{guests_with_licenses} of {total_guests} guest users have M365 licenses, potentially accessing Copilot with sensitive organizational data",
                    recommendation=f"Review {guests_with_licenses} guest user(s) with M365 licenses to verify Copilot access is intentional and appropriate. Guest users (B2B) can: 1) Use Copilot to search/summarize content they have access to (including shared Teams/SharePoint), 2) Generate content visible to internal users, 3) Access organizational knowledge through AI that may exceed intended collaboration scope. Implement quarterly access reviews for guest users, restrict guest access to specific sites/teams, and use sensitivity labels to prevent Copilot from accessing highly confidential content shared with guests. Consider dedicated guest licenses without Copilot for external collaboration scenarios.",
                    link_text="Manage Guest Access",
                    link_url="https://learn.microsoft.com/entra/external-id/what-is-b2b",
                    priority="Medium",
                    status="Action Required"
                ))
            elif total_guests > 10:
                # Informational: Many guests but no licenses
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"{total_guests} guest users in tenant, none with M365 licenses - external collaboration isolated from Copilot access",
                    recommendation="",
                    link_text="External Identities Overview",
                    link_url="https://learn.microsoft.com/entra/external-id/",
                    status="Success"
                ))
            
            # Observation 5: External sharing policy restrictions
            guest_invite_setting = b2b_metrics.get('guest_invite_restrictions', 'Unknown')

            
            # Convert enum to string if needed
            if not isinstance(guest_invite_setting, str):
                guest_invite_setting = str(guest_invite_setting)
            
            if guest_invite_setting == 'Unknown':
                pass  # Skip if data not available
            elif 'admins' not in guest_invite_setting.lower() and 'limited' not in guest_invite_setting.lower():
                # Action Required: Permissive guest invites
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"Guest user invitations are configured as '{guest_invite_setting}', allowing broad external access to Copilot-searchable content",
                    recommendation="Restrict guest user invitations to admins and specific users only to control external access to content that Copilot can search. Current permissive settings allow any user to invite guests who could access shared Teams channels, SharePoint sites, and OneDrive files - all searchable by Copilot. Unrestricted guest access risks: 1) Copilot exposing internal content to external users via AI summaries, 2) Guests discovering sensitive data through Copilot search beyond intended sharing, 3) Loss of data governance and compliance. Configure External collaboration settings to 'Only users assigned to specific admin roles can invite guest users' or implement guest access approval workflows.",
                    link_text="Configure External Collaboration",
                    link_url="https://learn.microsoft.com/entra/external-id/external-collaboration-settings-configure",
                    priority="Medium",
                    status="Action Required"
                ))
            else:
                # Success: Restrictive guest invites
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"Guest user invitations restricted to '{guest_invite_setting}', controlling external access to Copilot-searchable content",
                    recommendation="",
                    link_text="External Collaboration Settings",
                    link_url="https://learn.microsoft.com/entra/external-id/external-collaboration-settings-configure",
                    status="Success"
                ))
            
            # Observation 6: Cross-tenant access settings
            cross_tenant_configured = b2b_metrics.get('cross_tenant_access_configured', False)
            partner_count = b2b_metrics.get('partner_configurations', 0)
            
            if not cross_tenant_configured:
                # Action Required: No cross-tenant policies
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="Cross-tenant access settings not configured, allowing unrestricted B2B collaboration with external organizations accessing Copilot content",
                    recommendation="Configure cross-tenant access policies to control B2B collaboration with specific partner organizations and restrict Copilot data exposure. Without cross-tenant controls: 1) Users from any external org can access your Copilot-searchable content via B2B, 2) No control over which external tenants can collaborate, 3) Cannot enforce MFA or compliant devices for external users accessing Copilot content, 4) Risk of unintended data sharing through AI-powered search/summaries. Implement cross-tenant access settings to: allow/block specific partner organizations, require MFA for external users, restrict access to specific apps/resources. Essential for regulated industries and multi-tenant Copilot deployments.",
                    link_text="Cross-Tenant Access Settings",
                    link_url="https://learn.microsoft.com/entra/external-id/cross-tenant-access-overview",
                    priority="Medium",
                    status="Action Required"
                ))
            elif partner_count == 0:
                # Action Required: Cross-tenant configured but no partners defined
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="Cross-tenant access settings enabled but no partner organizations configured - default settings apply to all external tenants",
                    recommendation="Define specific partner organization policies to control which external tenants can collaborate and access Copilot content. With default settings only: 1) All external organizations have the same access level, 2) Cannot enforce different MFA requirements per partner, 3) Cannot block specific high-risk tenants, 4) No granular control over app access per partner. Add trusted partner organizations with specific inbound/outbound policies, require MFA for external users, and block risky tenants. Review Microsoft's recommended baseline policy.",
                    link_text="Configure Partner Organizations",
                    link_url="https://learn.microsoft.com/entra/external-id/cross-tenant-access-settings-b2b-collaboration",
                    priority="Medium",
                    status="Action Required"
                ))
            else:
                # Success: Cross-tenant policies configured with partners
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"Cross-tenant access policies configured with {partner_count} partner organization(s), governing external access to Copilot content",
                    recommendation="",
                    link_text="Cross-Tenant Access Settings",
                    link_url="https://learn.microsoft.com/entra/external-id/cross-tenant-access-overview",
                    status="Success"
                ))
            
            # Observation 7: Application Consent Settings
            consent_metrics = entra_insights.get('consent_summary', {})
            user_consent_allowed = consent_metrics.get('user_consent_allowed', False)
            admin_consent_required = consent_metrics.get('admin_consent_required', False)
            
            if user_consent_allowed and not admin_consent_required:
                # Action Required: User consent enabled
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="User consent enabled for applications, allowing users to grant apps access to Copilot-generated content and M365 data without admin review",
                    recommendation="Disable user consent and require admin approval for all application permissions to prevent unauthorized apps from accessing Copilot data. With user consent enabled, employees can: 1) Grant malicious apps access to their emails, files, Teams messages - all searchable by Copilot, 2) Approve apps that extract Copilot prompts/responses via Graph API, 3) Inadvertently share organizational knowledge with third-party services, 4) Create compliance violations (GDPR, HIPAA) through unvetted integrations. Configure consent settings to 'Do not allow user consent' and enable admin consent workflow so IT can review app permissions before granting access. This ensures only vetted applications interact with Copilot-accessible data.",
                    link_text="Configure User Consent",
                    link_url="https://learn.microsoft.com/entra/identity/enterprise-apps/configure-user-consent",
                    priority="High",
                    status="Action Required"
                ))
            elif admin_consent_required:
                # Success: Admin consent required
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="Admin consent required for applications, protecting Copilot data from unauthorized app access",
                    recommendation="",
                    link_text="Admin Consent Workflow",
                    link_url="https://learn.microsoft.com/entra/identity/enterprise-apps/configure-admin-consent-workflow",
                    status="Success"
                ))
            else:
                # Unable to determine consent settings - likely API permission issue
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="Application consent settings could not be verified - review tenant configuration to ensure proper app governance for Copilot data access",
                    recommendation="Review application consent policies in Entra ID to ensure user consent is appropriately restricted. Verify that: 1) Users cannot consent to apps accessing organizational data without admin review, 2) Admin consent workflow is enabled for user requests, 3) Only verified publishers and low-risk permissions are allowed for user consent (if enabled). This prevents unauthorized apps from accessing emails, files, and other content searchable by Copilot.",
                    link_text="Configure User Consent",
                    link_url="https://learn.microsoft.com/entra/identity/enterprise-apps/configure-user-consent",
                    priority="Medium",
                    status="Action Required"
                ))
            
            # Observation 8: Risky Application Permissions
            high_privilege_apps = consent_metrics.get('high_privilege_apps', 0)
            unverified_publishers = consent_metrics.get('unverified_publishers', 0)
            apps_with_graph = consent_metrics.get('apps_with_graph_access', 0)
            apps_with_mail = consent_metrics.get('apps_with_mail_access', 0)
            apps_with_files = consent_metrics.get('apps_with_files_access', 0)
            
            if high_privilege_apps > 0 or unverified_publishers > 0:
                risk_details = []
                if high_privilege_apps > 0:
                    risk_details.append(f"{high_privilege_apps} with high-privilege permissions")
                if unverified_publishers > 0:
                    risk_details.append(f"{unverified_publishers} from unverified publishers")
                if apps_with_graph > 0:
                    risk_details.append(f"{apps_with_graph} accessing Graph API (Copilot data)")
                
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"Risky applications detected: {', '.join(risk_details)} - potential unauthorized access to Copilot-generated content",
                    recommendation=f"Audit and restrict {high_privilege_apps + unverified_publishers} risky application(s) with access to M365 data and Copilot content. High-privilege apps can: 1) Read all emails and extract Copilot summaries ({apps_with_mail} apps with Mail.Read), 2) Access all SharePoint files and Copilot-indexed documents ({apps_with_files} apps with Files.Read), 3) Query Graph API to retrieve Copilot prompts and responses ({apps_with_graph} apps with Graph access), 4) Operate as unverified publishers without Microsoft validation ({unverified_publishers} apps). Review each app's permissions in Azure AD > Enterprise Applications > Permissions, revoke excessive permissions, and remove unnecessary apps. Implement app governance policies to detect risky permission grants automatically. Critical for preventing data exfiltration through third-party integrations.",
                    link_text="App Governance",
                    link_url="https://learn.microsoft.com/defender-cloud-apps/app-governance-manage-app-governance",
                    priority="High",
                    status="Action Required"
                ))
            else:
                # Success: No risky apps
                recommendations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation="No high-risk applications detected, all apps accessing M365 data have appropriate permissions and verified publishers",
                    recommendation="",
                    link_text="App Governance",
                    link_url="https://learn.microsoft.com/defender-cloud-apps/app-governance-manage-app-governance",
                    status="Success"
                ))
            
            # Observation 9: Access Reviews for Copilot Governance
            access_review_metrics = entra_insights.get('access_review_summary', {})
            if access_review_metrics:
                total_reviews = access_review_metrics.get('total_definitions', 0)
                active_reviews = access_review_metrics.get('active_reviews', 0)
                group_reviews = access_review_metrics.get('group_reviews', 0)
                role_reviews = access_review_metrics.get('role_reviews', 0)
                guest_reviews = access_review_metrics.get('guest_reviews', 0)
                recurring_reviews = access_review_metrics.get('recurring_reviews', 0)
                
                if total_reviews == 0:
                    # Action Required: No access reviews configured
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation="No access reviews configured - Copilot license assignments and privileged access not recertified",
                        recommendation="Implement quarterly access reviews for Copilot governance. Without reviews: 1) Former employees retain Copilot access after role changes, 2) Licenses remain assigned to inactive users (wasted cost), 3) Guest users maintain access to Copilot-searchable content indefinitely, 4) No compliance audit trail for who approved continued access. Configure reviews for: 1) Groups with Copilot licenses (quarterly recertification of members), 2) Guest user access to Teams/SharePoint (remove stale external accounts), 3) Privileged roles (Copilot admins, Teams admins - monthly reviews). Use automated approval for active users, require justification for continued access to high-value resources. Essential for SOC 2, ISO 27001, and cost optimization.",
                        link_text="Configure Access Reviews",
                        link_url="https://learn.microsoft.com/entra/id-governance/deploy-access-reviews",
                        priority="Medium",
                        status="Action Required"
                    ))
                elif recurring_reviews == 0:
                    # Action Required: Only one-time reviews
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"{total_reviews} access review(s) configured, but none are recurring - Copilot access not continuously governed",
                        recommendation=f"Convert {total_reviews} one-time access review(s) to recurring campaigns for continuous governance. One-time reviews: 1) Expire after completion (no ongoing oversight), 2) Require manual re-creation (administrative burden), 3) Create gaps in compliance coverage, 4) Miss new users added between reviews. Update review configurations to recur quarterly for group memberships, monthly for privileged roles, and semi-annually for guest access. Configure auto-apply results to automatically remove access for non-approved users. Set up notifications to reviewers 1 week before due date.",
                        link_text="Create Recurring Reviews",
                        link_url="https://learn.microsoft.com/entra/id-governance/create-access-review",
                        priority="Medium",
                        status="Action Required"
                    ))
                elif group_reviews == 0:
                    # Action Required: No group membership reviews for Copilot licenses
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"{total_reviews} access review(s) active ({recurring_reviews} recurring), but no group membership reviews for Copilot license governance",
                        recommendation=f"Add access reviews for groups that assign Copilot licenses to ensure only authorized users maintain access. Current reviews cover: {role_reviews} role(s), {guest_reviews} guest access. Missing: quarterly reviews of Copilot license groups to: 1) Recertify each member still needs Copilot access, 2) Remove users who changed roles or left organization, 3) Reclaim licenses for cost optimization, 4) Provide audit trail for compliance. Target groups with pattern 'Copilot-*' or 'M365-E5-*', assign managers as reviewers, enable auto-removal of denied users. Saves ~15-20% on license costs by removing inactive assignments.",
                        link_text="Review Group Memberships",
                        link_url="https://learn.microsoft.com/entra/id-governance/create-access-review",
                        priority="Medium",
                        status="Action Required"
                    ))
                else:
                    # Success: Comprehensive access reviews configured
                    review_types = []
                    if group_reviews > 0:
                        review_types.append(f"{group_reviews} group")
                    if role_reviews > 0:
                        review_types.append(f"{role_reviews} role")
                    if guest_reviews > 0:
                        review_types.append(f"{guest_reviews} guest")
                    
                    recommendations.append(new_recommendation(
                        service="Entra",
                        feature=feature_name,
                        observation=f"{active_reviews} active access review(s) ({', '.join(review_types)}), {recurring_reviews} recurring - continuous governance for Copilot access",
                        recommendation="",
                        link_text="Access Review Best Practices",
                        link_url="https://learn.microsoft.com/entra/id-governance/deploy-access-reviews",
                        status="Success"
                    ))
        
        return recommendations
    
    # Non-Success: Keep original license-check recommendation unchanged
    return new_recommendation(
        service="Entra",
        feature=feature_name,
        observation=f"{feature_name} is {status} in {friendly_sku}, preventing advanced identity protection for AI services",
        recommendation=f"Enable {feature_name} to leverage Privileged Identity Management (PIM) for just-in-time Copilot admin access, implement access reviews for users with Copilot licenses, and protect against identity-based attacks targeting AI assistants with advanced risk detection.",
        link_text="Identity Governance for Copilot Admins",
        link_url="https://learn.microsoft.com/entra/id-governance/identity-governance-overview",
        priority="High",
        status=status
    )
