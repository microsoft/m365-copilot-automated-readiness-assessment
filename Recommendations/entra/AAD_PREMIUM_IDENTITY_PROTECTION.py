"""
Entra Identity Protection - Enhanced with Risk Detection Analysis
Provides license check + risky user detection + risk-based policy recommendations for Copilot security.
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Generate Identity Protection recommendations with risk analysis.
    
    Returns multiple observations:
    1. License check (with upgrade path for lower SKUs)
    2. Risky users detection (if entra_insights available):
       - Confirmed compromised: High priority - Immediate action
       - At risk users: Medium priority - Investigation needed
       - No risky users: Success
    3. Risk-based CA policy status
    
    Args:
        sku_name: SKU name where feature is found
        status: Provisioning status
        client: Graph client (unused, for compatibility)
        entra_insights: Pre-computed identity metrics with risk_metrics
    """
    feature_name = "Entra Identity Protection"
    friendly_sku = get_friendly_sku_name(sku_name)
    observations = []
    
    # ========================================
    # OBSERVATION 1: License Check
    # ========================================
    if status == "Success":
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, detecting risky Copilot access patterns and compromised accounts",
            recommendation="",
            link_text="Protect Against AI Misuse",
            link_url="https://learn.microsoft.com/entra/id-protection/",
            status=status
        ))
    else:
        # License not available - drive upgrade for Copilot security
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku} - upgrade required to detect compromised accounts accessing Copilot",
            recommendation=f"Upgrade to Microsoft 365 E5 or Microsoft Entra ID P2 to enable Identity Protection for Copilot security. Without risk detection, compromised accounts can use Copilot undetected to: 1) Exfiltrate sensitive data through AI prompts, 2) Access confidential documents via Copilot's search capabilities, 3) Generate summaries of proprietary information, 4) Operate during off-hours without triggering alerts. Identity Protection automatically detects: leaked credentials, impossible travel patterns, unfamiliar sign-in properties, anonymous IP usage, and malware-linked activity. Integrates with Conditional Access to automatically block high-risk Copilot access. Essential for preventing AI-enabled data breaches and insider threats.",
            link_text="Identity Protection Overview",
            link_url="https://learn.microsoft.com/entra/id-protection/overview-identity-protection",
            priority="High",
            status=status
        ))
    
    # ========================================
    # OBSERVATION 2: Risky Users Detection
    # ========================================
    if entra_insights and status == "Success":
        risk_metrics = entra_insights.get('risk_metrics', {})
        confirmed_compromised = risk_metrics.get('confirmed_compromised_users', 0)
        at_risk = risk_metrics.get('at_risk_users', 0)
        total_risky = risk_metrics.get('total_risky_users', 0)
        
        # Confirmed compromised users - immediate action required
        if confirmed_compromised > 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"{confirmed_compromised} confirmed compromised user(s) detected - immediate security incident requiring Copilot access revocation",
                recommendation=f"URGENT: {confirmed_compromised} user account(s) confirmed as compromised with potential Copilot access. Immediate actions: 1) Revoke all sessions and force re-authentication, 2) Reset passwords and require MFA registration, 3) Review Copilot audit logs for data exfiltration (prompts submitted, documents accessed, summaries generated), 4) Block Copilot access until security clearance, 5) Investigate: What sensitive data did compromised accounts access via Copilot? What prompts were submitted? Were files downloaded or shared? Compromised accounts with Copilot access can systematically extract organizational knowledge through AI-powered search and summarization. Treat as active data breach.",
                link_text="Respond to Compromised Accounts",
                link_url="https://learn.microsoft.com/entra/id-protection/howto-identity-protection-investigate-risk",
                priority="High",
                status=status
            ))
        
        # At-risk users detected - investigation needed
        elif at_risk > 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"{at_risk} at-risk user(s) detected with suspicious sign-in patterns - potential Copilot security threat",
                recommendation=f"Investigate {at_risk} at-risk user account(s) for potential compromise before they access Copilot with sensitive data: 1) Review risk detections: unfamiliar locations, impossible travel, anonymous IPs, leaked credentials, 2) Check recent Copilot activity: unusual prompt patterns, off-hours usage, excessive data access, 3) Require MFA re-authentication for Copilot access, 4) Consider temporary Copilot access restriction until risk is remediated. Create Conditional Access policy to block high/medium risk users from Microsoft 365 apps. Early detection prevents compromised accounts from using AI to exfiltrate data.",
                link_text="Investigate Risk Detections",
                link_url="https://learn.microsoft.com/entra/id-protection/howto-identity-protection-investigate-risk",
                priority="Medium",
                status=status
            ))
        
        # No risky users - good security posture
        else:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="No risky users detected, Identity Protection is actively monitoring and protecting accounts",
                recommendation="",
                link_text="Identity Protection Best Practices",
                link_url="https://learn.microsoft.com/entra/id-protection/overview-identity-protection",
                status=status
            ))
    
    # ========================================
    # OBSERVATION 3: Risk-Based CA Policies
    # ========================================
    if entra_insights and status == "Success":
        risk_metrics = entra_insights.get('risk_metrics', {})
        user_risk_policy_exists = risk_metrics.get('user_risk_policy_exists', False)
        signin_risk_policy_exists = risk_metrics.get('signin_risk_policy_exists', False)
        
        # No risk-based policies configured
        if not user_risk_policy_exists and not signin_risk_policy_exists:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="Identity Protection enabled but no risk-based Conditional Access policies configured to protect Copilot",
                recommendation="Create risk-based Conditional Access policies to automatically block or require re-authentication for risky Copilot access: 1) User risk policy: Block high-risk users, require password change for medium-risk users before Copilot access, 2) Sign-in risk policy: Block high-risk sign-ins, require MFA for medium-risk sign-ins accessing Microsoft 365 apps. Target 'Office 365' application to include Copilot. This prevents compromised accounts from accessing AI capabilities even if credentials are stolen. Test in report-only mode first.",
                link_text="Risk-Based Conditional Access",
                link_url="https://learn.microsoft.com/entra/id-protection/howto-identity-protection-configure-risk-policies",
                priority="Medium",
                status=status
            ))
    
    return observations
