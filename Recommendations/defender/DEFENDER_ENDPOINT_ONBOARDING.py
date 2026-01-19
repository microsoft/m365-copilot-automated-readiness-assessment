"""
Microsoft Defender for Endpoint - Device Onboarding Status
Checks if Defender for Endpoint API is accessible and devices are onboarded
"""
from new_recommendation import new_recommendation


async def get_recommendation(client, defender_client=None, services_and_licenses=None, purview_client=None):
    """
    Check if Defender for Endpoint is properly onboarded with devices
    
    When Defender for Endpoint returns 403 Forbidden, it typically means:
    1. License is active but no devices are onboarded yet
    2. API access requires at least one device reporting to the service
    
    This recommendation alerts users to onboard devices to unlock full API capabilities.
    """
    
    # Check if defender_client is available and if Defender API is working
    if defender_client is None:
        return new_recommendation(
            service="Defender",
            feature="Defender for Endpoint - Device Onboarding",
            status="Warning",
            priority="High",
            observation=(
                "**Defender client not initialized.** Unable to assess device onboarding status."
            ),
            recommendation=(
                "Ensure Defender for Endpoint license is assigned and service principal has required permissions "
                "(Machine.Read.All, Incident.Read.All). Re-run the tool after configuration."
            ),
            link_text="Set up Defender for Endpoint",
            link_url="https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/onboarding"
        )
    
    # Check if Defender API is unavailable (403 errors)
    if not defender_client.available:
        # API returned 403 - most likely no devices onboarded
        # Build list of unavailable features based on what's actually missing
        unavailable_features = []
        
        # Check what's actually missing from defender_client
        if not defender_client.defender_incidents:
            unavailable_features.append("  • **Incidents** - Security incident tracking and correlation")
        if not defender_client.defender_devices:
            unavailable_features.append("  • **Machines/Devices** - Device inventory and health monitoring")
        if not defender_client.defender_vulnerabilities:
            unavailable_features.append("  • **Vulnerabilities** - Security weakness assessment and prioritization")
        if not defender_client.advanced_hunting_results:
            unavailable_features.append("  • **Advanced Hunting** - Custom threat detection queries (4 Copilot-specific queries)")
        if not defender_client.security_recommendations:
            unavailable_features.append("  • **Security Recommendations** - Configuration improvement suggestions")
        if not defender_client.software_inventory:
            unavailable_features.append("  • **Software Inventory** - Application discovery and version tracking")
        if not defender_client.exposure_score or not defender_client.exposure_score:
            unavailable_features.append("  • **Exposure Score** - Overall security posture measurement")
        
        unavailable_list = "\n".join(unavailable_features) if unavailable_features else "  • All Defender for Endpoint capabilities"
        feature_count = len(unavailable_features) if unavailable_features else 7
        
        # Check for missing features (404 errors - not licensed)
        missing_note = ""
        if defender_client.missing_features:
            feature_map = {
                'email_threats': 'Email Post-Delivery Detections (advanced email threat analysis)'
            }
            missing_list = [f"  • {feature_map.get(f, f)}" for f in defender_client.missing_features]
            missing_note = (
                f"\n\n**Additionally, {len(defender_client.missing_features)} feature(s) not available in your license:**\n" +
                "\n".join(missing_list) +
                "\n\nThese features require Defender for Office 365 Plan 2 or Microsoft 365 E5 Security."
            )
        
        return new_recommendation(
            service="Defender",
            feature="Defender for Endpoint - Device Onboarding",
            status="Critical",
            priority="High",
            observation=(
                f"**{feature_count} Microsoft Defender for Endpoint capabilities unavailable (403 Forbidden).**\n\n"
                "**Root Cause:** No devices are onboarded to Defender for Endpoint. "
                "The API requires at least one device reporting to the service before it will respond to queries.\n\n"
                "**Unavailable Features:**\n"
                f"{unavailable_list}\n\n"
                "**Note:** All these features share the same root cause and will become available simultaneously "
                f"once you onboard at least one device.{missing_note}"
            ),
            recommendation=(
                "**Onboard at least one device to Microsoft Defender for Endpoint:**\n\n"
                "1. Go to Microsoft 365 Defender portal: https://security.microsoft.com\n"
                "2. Navigate to **Settings** → **Endpoints** → **Onboarding**\n"
                "3. Select deployment method (Local Script for testing, Group Policy/Intune for production)\n"
                "4. Download onboarding package and deploy to Windows devices\n"
                "5. Wait 5-10 minutes for device to appear in portal\n"
                "6. Re-run this tool to access full Defender API capabilities\n\n"
                "**For production deployment:** Use Intune, Group Policy, or SCCM to onboard devices at scale.\n\n"
                "**Note:** Service principal already has correct API permissions (Machine.Read.All, Incident.Read.All). "
                "Once devices are onboarded, all API endpoints will become accessible."
            ),
            link_text="Onboard devices to Defender for Endpoint",
            link_url="https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/onboarding"
        )
    
    # Defender API is working - check device count
    machines_count = defender_client.device_summary.get('total', 0) if defender_client.device_summary else 0
    
    if machines_count == 0:
        # API works but no devices (shouldn't happen, but defensive check)
        return new_recommendation(
            service="Defender",
            feature="Defender for Endpoint - Device Onboarding",
            status="Warning",
            priority="Medium",
            observation=(
                f"**Defender for Endpoint is active but no devices are reporting.**\n\n"
                "API is accessible but device inventory is empty. This limits threat detection capabilities."
            ),
            recommendation=(
                "Onboard devices to Defender for Endpoint to enable full security monitoring. "
                "See Settings → Endpoints → Onboarding in Microsoft 365 Defender portal."
            ),
            link_text="Device onboarding guide",
            link_url="https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/onboarding"
        )
    elif machines_count < 10:
        # Few devices onboarded - suggest scaling up
        return new_recommendation(
            service="Defender",
            feature="Defender for Endpoint - Device Onboarding",
            status="Success",
            priority="Low",
            observation=(
                f"**{machines_count} device(s) onboarded** to Defender for Endpoint.\n\n"
                "API is fully functional. Consider onboarding additional devices for comprehensive security coverage."
            ),
            recommendation=(
                "Review device inventory to ensure all critical endpoints are protected. "
                "Use Intune or Group Policy to automate onboarding at scale for production environments."
            ),
            link_text="Scale Defender for Endpoint deployment",
            link_url="https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/deployment-phases"
        )
    else:
        # Good device coverage
        return new_recommendation(
            service="Defender",
            feature="Defender for Endpoint - Device Onboarding",
            status="Success",
            priority="Low",
            observation=(
                f"**{machines_count} devices onboarded** to Defender for Endpoint. API is fully operational."
            ),
            recommendation=(
                "Device onboarding is healthy. Continue monitoring device compliance and onboard new devices as they join the environment."
            ),
            link_text="Monitor device health",
            link_url="https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/device-health-sensor-health-os"
        )
