"""
Microsoft Defender XDR Activation - Prerequisite Recommendation
"""
from new_recommendation import new_recommendation

def get_recommendation(defender_client=None, defender_plans=None):
    """
    Check if Microsoft Defender XDR needs to be activated OR licensed.
    
    Two scenarios:
    1. Has XDR license but not activated → High priority: Activate it
    2. No XDR license (lower SKU) → High priority: Get the license
    """
    feature_name = "Microsoft Defender XDR"
    
    # Check if tenant has XDR license (MTP service plan)
    has_xdr_license = False
    has_any_defender = False
    
    if defender_plans:
        for lic in defender_plans:
            has_any_defender = True  # They have some Defender features
            for plan in lic.get('service_plans', []):
                plan_name = plan.get('name', '')
                # MTP is the XDR service plan
                if plan_name == 'MTP':
                    has_xdr_license = True
                    break
            if has_xdr_license:
                break
    
    # Scenario 1: Has XDR license but APIs show not activated
    if has_xdr_license and defender_client and defender_client.activation_needed:
        activation_msg = defender_client.activation_message or "Microsoft Defender XDR not activated"
        
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=f"{activation_msg} - Security APIs unavailable despite having MTP (XDR) license",
            recommendation="Activate Microsoft Defender XDR in the Security portal to enable unified security monitoring, threat detection, and incident response across your Microsoft 365 environment. This is required to access security data through APIs and protect Copilot workloads with advanced threat protection, prompt injection detection, and automated security responses.",
            link_text="Activate Microsoft Defender XDR",
            link_url="https://security.microsoft.com",
            priority="High",
            status="Missing Prerequisite"
        )
    
    # Scenario 2: No XDR license but has other Defender features (Business Premium, E3)
    # Show recommendation to upgrade to get XDR
    elif has_any_defender and not has_xdr_license:
        return new_recommendation(
            service="Defender",
            feature=feature_name,
            observation=f"{feature_name} license not found - current SKU has limited Defender capabilities without unified XDR",
            recommendation="Upgrade to Microsoft 365 E5 or add Microsoft Defender plan to get XDR (Extended Detection and Response) capabilities. XDR provides unified security monitoring across endpoints, identities, email, and cloud apps with advanced threat hunting, automated investigation, and AI-powered security responses essential for protecting Copilot workloads from sophisticated attacks.",
            link_text="Microsoft Defender XDR Licensing",
            link_url="https://learn.microsoft.com/microsoft-365/security/defender/microsoft-365-defender",
            priority="High",
            status="Missing"
        )
    
    # Scenario 3: No Defender at all - this gets handled elsewhere in get_defender_info.py
    # (returns early before calling this function)
    
    # Return None if XDR is licensed and activated (APIs working)
    return None
