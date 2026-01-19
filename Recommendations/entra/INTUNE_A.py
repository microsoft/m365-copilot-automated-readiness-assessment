"""
Microsoft Intune (Plan A) - Enhanced with Device Compliance Analysis
Provides license check + device compliance state + CA integration for Copilot device security.
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Generate Intune recommendations with device compliance analysis for Copilot security.
    
    Returns multiple observations:
    1. License check (with upgrade path for lower SKUs)
    2. Device compliance analysis (if entra_insights available):
       - Non-compliant devices accessing Copilot: High priority
       - No managed devices (BYOD): Medium priority
       - Good compliance: Success
    3. CA integration check - Verify compliant device requirement for Copilot
    
    Args:
        sku_name: SKU name where feature is found
        status: Provisioning status
        client: Graph client (unused, for compatibility)
        entra_insights: Pre-computed identity metrics with device_summary
    """
    feature_name = "Microsoft Intune (Plan A)"
    friendly_sku = get_friendly_sku_name(sku_name)
    observations = []
    
    # ========================================
    # OBSERVATION 1: License Check
    # ========================================
    if status == "Success":
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, managing devices that access M365 Copilot with comprehensive security policies",
            recommendation="",
            link_text="Microsoft 365 Documentation",
            link_url="https://learn.microsoft.com/microsoft-365/",
            status=status
        ))
    else:
        # License not available - drive upgrade for device management
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku} - upgrade required for device compliance enforcement",
            recommendation=f"Upgrade to Microsoft 365 E3/E5 or Business Premium to enable Intune for Copilot device security. Without device management, users can access Copilot from: 1) Personal unmanaged devices where data can be copied/screenshot without DLP, 2) Non-compliant devices with malware that could intercept Copilot prompts/responses, 3) Jailbroken/rooted devices bypassing security controls, 4) Devices without encryption exposing Copilot data if lost/stolen. Intune allows you to: require device encryption and PIN, deploy compliance policies blocking non-compliant device access, wipe corporate data from lost devices, prevent copy/paste from Copilot on personal devices. Essential for preventing Copilot data leakage through unmanaged endpoints.",
            link_text="Intune Overview",
            link_url="https://learn.microsoft.com/mem/intune/fundamentals/what-is-intune",
            priority="High",
            status=status
        ))
    
    # ========================================
    # OBSERVATION 2: Device Compliance State
    # ========================================
    if entra_insights and status == "Success":
        device_summary = entra_insights.get('device_summary', {})
        total_devices = device_summary.get('total_managed_devices', 0)
        compliant_devices = device_summary.get('compliant_devices', 0)
        non_compliant_devices = device_summary.get('non_compliant_devices', 0)
        
        # No managed devices - BYOD risk
        if total_devices == 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="No managed devices detected - users may access Copilot from unmanaged BYOD devices",
                recommendation="Enroll devices in Intune to enforce compliance policies for Copilot access. Unmanaged devices pose risks: 1) No encryption enforcement - Copilot data at risk if device lost, 2) No malware protection - keyloggers could capture AI prompts containing sensitive info, 3) No DLP controls - users can screenshot/copy Copilot responses to personal apps, 4) No remote wipe - cannot remove corporate data if employee leaves. Start with company-owned devices, then implement MAM (Mobile Application Management) for BYOD scenarios to protect Copilot within managed apps without full device control.",
                link_text="Device Enrollment",
                link_url="https://learn.microsoft.com/mem/intune/enrollment/",
                priority="Medium",
                status=status
            ))
        
        # Non-compliant devices detected
        elif non_compliant_devices > 0:
            compliance_rate = (compliant_devices / total_devices * 100) if total_devices > 0 else 0
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"{non_compliant_devices} of {total_devices} managed devices ({100-compliance_rate:.1f}%) are non-compliant - may access Copilot despite policy violations",
                recommendation=f"Block Copilot access from {non_compliant_devices} non-compliant device(s) using Conditional Access. Non-compliant devices fail security requirements: missing encryption, outdated OS, disabled antivirus, jailbroken/rooted, or policy violations. These devices can: 1) Leak Copilot responses through screenshots on unencrypted storage, 2) Be compromised by malware intercepting AI prompts, 3) Violate compliance frameworks (HIPAA, SOC 2) requiring device security. Create CA policy targeting Microsoft 365 requiring 'Require device to be marked as compliant'. Review non-compliance reasons in Intune console and remediate or block access.",
                link_text="Require Compliant Devices",
                link_url="https://learn.microsoft.com/mem/intune/protect/device-compliance-get-started",
                priority="High",
                status=status
            ))
        
        # Good compliance
        else:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"{compliant_devices} of {total_devices} managed devices (100%) are compliant, enforcing security policies for Copilot access",
                recommendation="",
                link_text="Device Compliance Best Practices",
                link_url="https://learn.microsoft.com/mem/intune/protect/device-compliance-get-started",
                status=status
            ))
    
    # ========================================
    # OBSERVATION 3: CA Integration Check
    # ========================================
    if entra_insights and status == "Success":
        device_summary = entra_insights.get('device_summary', {})
        ca_requires_compliance = device_summary.get('ca_requires_compliance', False)
        total_devices = device_summary.get('total_managed_devices', 0)
        
        # Has managed devices but CA doesn't require compliance
        if total_devices > 0 and not ca_requires_compliance:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"{total_devices} devices managed by Intune, but Conditional Access does not require compliant devices for Copilot",
                recommendation="Create Conditional Access policy to require compliant devices for Microsoft 365 apps (including Copilot). Currently, non-compliant devices can bypass Intune security policies and access Copilot. Configure: Target 'Office 365' application, Grant 'Require device to be marked as compliant', Apply to all users with Copilot licenses. This ensures only encrypted, malware-protected, policy-compliant devices can access AI capabilities, preventing data leakage through compromised endpoints.",
                link_text="Device Compliance with CA",
                link_url="https://learn.microsoft.com/entra/identity/conditional-access/howto-conditional-access-policy-compliant-device",
                priority="Medium",
                status=status
            ))
        
        # CA properly requires compliance - success observation
        elif total_devices > 0 and ca_requires_compliance:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"Conditional Access requires compliant devices for Microsoft 365 apps, enforcing Intune policies for Copilot access",
                recommendation="",
                link_text="Device Compliance with CA",
                link_url="https://learn.microsoft.com/entra/identity/conditional-access/howto-conditional-access-policy-compliant-device",
                status=status
            ))
    
    return observations
