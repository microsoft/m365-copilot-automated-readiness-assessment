"""
Conditional Access (Entra ID P1) - Enhanced with Policy Configuration Analysis
Provides license check + CA policy coverage, MFA enforcement, and Copilot-specific targeting analysis.
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Generate Conditional Access recommendations with policy analysis.
    
    Returns multiple observations:
    1. License check (unchanged - existing behavior)
    2. CA policy configuration analysis (if entra_insights available):
       - No policies: High priority - Create baseline policies
       - Policies exist but no MFA: Medium priority - Add MFA requirements
       - Policies with MFA: Success with detailed metrics
    3. Copilot-specific targeting check
    
    Args:
        sku_name: SKU name where feature is found
        status: Provisioning status
        client: Graph client (unused, for compatibility)
        entra_insights: Pre-computed identity metrics with ca_metrics
    """
    feature_name = "Conditional Access"
    friendly_sku = get_friendly_sku_name(sku_name)
    observations = []
    
    # ========================================
    # OBSERVATION 1: License Check
    # ========================================
    if status == "Success":
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling context-aware access policies for Copilot",
            recommendation="",
            link_text="Policy-Based Copilot Access",
            link_url="https://learn.microsoft.com/entra/identity/conditional-access/",
            status=status
        ))
    else:
        # License not available - drive upgrade for Copilot security
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku} - upgrade required to secure Copilot with context-aware policies",
            recommendation=f"Upgrade to Microsoft 365 Business Premium, E3, or E5 to enable Conditional Access for Copilot security. Without CA, any authenticated user can access Copilot regardless of device compliance, location risk, or sign-in risk - exposing your organization to data exfiltration through AI prompts from unmanaged devices or compromised accounts. Conditional Access allows you to: 1) Require MFA for Copilot access, 2) Block Copilot from unmanaged/non-compliant devices, 3) Restrict access from untrusted locations or high-risk sign-ins, 4) Enforce device compliance policies. Essential security layer for organizations deploying AI assistants with access to sensitive data.",
            link_text="Conditional Access Overview",
            link_url="https://learn.microsoft.com/entra/identity/conditional-access/overview",
            priority="High",
            status=status
        ))
    
    # ========================================
    # OBSERVATION 2: CA Policy Coverage
    # ========================================
    if entra_insights and status == "Success":
        ca_metrics = entra_insights.get('ca_metrics', {})
        total_policies = ca_metrics.get('total_policies', 0)
        enabled_policies = ca_metrics.get('enabled_policies', 0)
        require_mfa = ca_metrics.get('policies_requiring_mfa', 0)
        target_all_apps = ca_metrics.get('policies_targeting_all_apps', 0)
        target_m365 = ca_metrics.get('policies_targeting_m365', 0)
        block_legacy_auth = ca_metrics.get('policies_blocking_legacy_auth', 0)
        
        # No policies configured
        if total_policies == 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="No Conditional Access policies configured, leaving Copilot accessible from any device, location, or risk level",
                recommendation="Create baseline Conditional Access policies for Microsoft 365 apps to protect Copilot: 1) Require MFA for all cloud apps, 2) Block legacy authentication that bypasses modern security, 3) Require compliant or hybrid-joined devices for Copilot access, 4) Block access from high-risk locations. Start with report-only mode, monitor for 2 weeks, then enforce. Without CA policies, compromised credentials can access Copilot to exfiltrate data.",
                link_text="CA Policies for Copilot",
                link_url="https://learn.microsoft.com/entra/identity/conditional-access/concept-conditional-access-cloud-apps",
                priority="High",
                status=status
            ))
        
        # Policies exist but no MFA enforcement
        elif require_mfa == 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"{enabled_policies} Conditional Access policy(ies) configured, but none require MFA for Microsoft 365 apps",
                recommendation="Update Conditional Access policies to require MFA for all Microsoft 365 applications, including Copilot. Without MFA enforcement, stolen passwords grant full access to AI assistants that can retrieve sensitive organizational data. Create a CA policy targeting 'Office 365' app with grant control 'Require multi-factor authentication'. Apply to all users or start with Copilot-licensed users.",
                link_text="Require MFA with CA",
                link_url="https://learn.microsoft.com/entra/identity/conditional-access/howto-conditional-access-policy-all-users-mfa",
                priority="Medium",
                status=status
            ))
        
        # Policies configured with good coverage
        else:
            policy_details = f"{enabled_policies} enabled policy(ies), {require_mfa} requiring MFA"
            if target_m365 > 0:
                policy_details += f", {target_m365} targeting Microsoft 365 apps"
            if block_legacy_auth > 0:
                policy_details += f", {block_legacy_auth} blocking legacy authentication"
            
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"Conditional Access protecting Microsoft 365: {policy_details}",
                recommendation="",
                link_text="CA Best Practices",
                link_url="https://learn.microsoft.com/entra/identity/conditional-access/plan-conditional-access",
                status=status
            ))
    
    # ========================================
    # OBSERVATION 3: Copilot-Specific Targeting
    # ========================================
    if entra_insights and status == "Success":
        ca_metrics = entra_insights.get('ca_metrics', {})
        total_policies = ca_metrics.get('total_policies', 0)
        target_m365 = ca_metrics.get('policies_targeting_m365', 0)
        
        # Only show if policies exist but none target M365 apps specifically
        if total_policies > 0 and target_m365 == 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"{total_policies} Conditional Access policy(ies) configured, but none specifically target Copilot applications",
                recommendation="Create Copilot-specific Conditional Access policies targeting Microsoft 365 Copilot and Graph Connector applications. Apply stricter controls for AI access: require compliant devices, trusted locations, and MFA. Consider blocking Copilot access from unmanaged devices to prevent data exfiltration. Target these apps: 'Office 365' (includes Copilot), 'Microsoft Graph' connectors.",
                link_text="Conditional Access for Copilot",
                link_url="https://learn.microsoft.com/entra/identity/conditional-access/concept-conditional-access-cloud-apps",
                priority="Medium",
                status=status
            ))
    
    return observations
