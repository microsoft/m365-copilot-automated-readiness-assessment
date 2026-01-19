"""
Microsoft Entra Internet Access - Enhanced with Secure Web Gateway Analysis
Provides license check + traffic monitoring + web filtering for AI services and Copilot.
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

def get_recommendation(sku_name, status="Success", client=None, entra_insights=None):
    """
    Generate Entra Internet Access recommendations with secure web gateway analysis.
    
    Entra Internet Access (part of Global Secure Access) provides:
    - Secure web gateway for internet traffic including AI services
    - Traffic visibility for Microsoft 365 and third-party AI tools
    - Web content filtering to block unauthorized AI platforms
    - DLP and threat protection for Copilot internet traffic
    
    Returns multiple observations:
    1. License check (with upgrade path for lower SKUs)
    2. Web content filtering configuration (if entra_insights available):
       - Policies configured: Success with policy count
       - No policies: Medium priority - Configure filtering
    3. Traffic forwarding status (M365/Internet traffic)
    
    Args:
        sku_name: SKU name where feature is found
        status: Provisioning status
        client: Graph client (unused, for compatibility)
        entra_insights: Pre-computed security metrics with network_access_summary
    """
    feature_name = "Microsoft Entra Internet Access"
    friendly_sku = get_friendly_sku_name(sku_name)
    observations = []
    
    # ========================================
    # OBSERVATION 1: License Check
    # ========================================
    if status == "Success":
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing secure web gateway with AI service visibility and threat protection",
            recommendation="",
            link_text="Secure Internet Gateway for AI",
            link_url="https://learn.microsoft.com/entra/global-secure-access/",
            status=status
        ))
    else:
        # License not available - drive upgrade for AI security
        observations.append(new_recommendation(
            service="Entra",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku} - upgrade required for comprehensive AI traffic security",
            recommendation=f"Upgrade to Microsoft Entra Suite or Security Service Edge to enable Internet Access for AI security. Without secure web gateway, you cannot: 1) Detect shadow AI usage - employees using ChatGPT, Claude, Gemini to process corporate data outside M365 Copilot governance, 2) Monitor Copilot data exfiltration - users copying AI summaries to personal cloud storage or unauthorized AI platforms, 3) Block unauthorized AI tools - prevent employees from uploading sensitive documents to consumer AI services, 4) Inspect AI traffic for malware - detect credential harvesting or phishing via malicious AI tool sites. Internet Access provides: traffic visibility showing which AI services users access, web content filtering to block/warn for unauthorized AI platforms, DLP inspection of traffic to/from AI services, conditional access integration to enforce device compliance for AI access. Essential for preventing data leakage through AI tools outside your security perimeter.",
            link_text="Global Secure Access Overview",
            link_url="https://learn.microsoft.com/entra/global-secure-access/overview-what-is-global-secure-access",
            priority="Medium",
            status=status
        ))
    
    # ========================================
    # OBSERVATION 2: Web Content Filtering Configuration
    # ========================================
    if entra_insights:
        network_summary = entra_insights.get('network_access_summary', {})
        network_status = network_summary.get('status', 'Success')
        
        # Check if API returned an error (permission denied or not licensed)
        if network_status == 'NotLicensed':
            # Generate license recommendation
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="Global Secure Access (Entra Internet Access) is not enabled in your tenant",
                recommendation="Enable Global Secure Access to protect against Shadow AI and unauthorized cloud service usage. This feature provides: 1) Web content filtering to block unauthorized AI platforms (ChatGPT, Claude, Gemini), 2) Traffic forwarding for DLP inspection of AI tool usage, 3) Conditional access integration to enforce device compliance for AI access, 4) Real-time visibility into which AI services employees access. Without Global Secure Access, you cannot control or monitor user access to external AI services, increasing risks of data leakage, compliance violations, and unauthorized AI tool usage. Requires Entra Suite or standalone Global Secure Access license.",
                link_text="What is Global Secure Access?",
                link_url="https://learn.microsoft.com/entra/global-secure-access/overview-what-is-global-secure-access",
                priority="Medium",
                status="Not Licensed"
            ))
            return observations
        elif network_status == 'PermissionDenied':
            # Generate permission recommendation
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="NetworkAccessPolicy.Read.All permission is not granted to the service principal",
                recommendation="Grant the NetworkAccessPolicy.Read.All API permission to enable Global Secure Access monitoring. This permission allows the tool to assess your web content filtering policies, traffic forwarding rules, and AI security controls. Run the setup-service-principal.ps1 script to configure required permissions, then rerun this assessment to generate Global Secure Access observations.",
                link_text="NetworkAccessPolicy Permission Reference",
                link_url="https://learn.microsoft.com/graph/permissions-reference#networkaccesspolicyreadall",
                priority="Low",
                status="Permission Required"
            ))
            return observations
        elif network_status == 'Error':
            # API error - skip remaining observations
            return observations
        
        # Success - proceed with normal observations
        total_filtering_policies = network_summary.get('total_filtering_policies', 0)
        web_filtering_enabled = network_summary.get('web_filtering_enabled', False)
        fqdn_rules = network_summary.get('fqdn_rules_count', 0)
        web_category_rules = network_summary.get('web_category_rules_count', 0)
        
        # No filtering policies configured
        if total_filtering_policies == 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="Global Secure Access deployed, but no web content filtering policies configured to block unauthorized AI platforms",
                recommendation="Configure web content filtering policies to control AI service access and prevent shadow AI usage: 1) Block consumer AI platforms (ChatGPT free tier, Claude web, Gemini) to prevent uncontrolled data sharing outside M365 Copilot, 2) Create FQDN allow/block lists for approved AI research tools vs unauthorized services, 3) Use web category filtering to block 'AI/ML' or 'Generative AI' categories except approved URLs, 4) Enforce conditional access for AI services - require compliant devices and MFA for any AI tool access. Without filtering, employees can bypass M365 Copilot governance and upload sensitive documents to consumer AI tools. Configure rules in Global Secure Access portal and provide user education: 'For AI assistance with work data, use M365 Copilot - external AI tools are blocked for security.'",
                link_text="Configure Web Content Filtering",
                link_url="https://learn.microsoft.com/entra/global-secure-access/how-to-configure-web-content-filtering",
                priority="Medium",
                status=status
            ))
        
        # Filtering policies configured - show metrics
        else:
            policy_details = f"{total_filtering_policies} web filtering policy(ies) configured"
            if fqdn_rules > 0:
                policy_details += f", {fqdn_rules} FQDN rule(s)"
            if web_category_rules > 0:
                policy_details += f", {web_category_rules} web category rule(s)"
            
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation=f"Web content filtering active: {policy_details}, controlling access to AI platforms and detecting shadow AI usage",
                recommendation="",
                link_text="Web Filtering Best Practices",
                link_url="https://learn.microsoft.com/entra/global-secure-access/how-to-configure-web-content-filtering",
                status=status
            ))
    
    # ========================================
    # OBSERVATION 3: Traffic Forwarding Configuration
    # ========================================
    if entra_insights:
        network_summary = entra_insights.get('network_access_summary', {})
        total_forwarding_profiles = network_summary.get('total_forwarding_profiles', 0)
        m365_forwarding = network_summary.get('m365_traffic_forwarding', False)
        internet_forwarding = network_summary.get('internet_traffic_forwarding', False)
        
        # No traffic forwarding configured
        if total_forwarding_profiles == 0:
            observations.append(new_recommendation(
                service="Entra",
                feature=feature_name,
                observation="Global Secure Access deployed, but no traffic forwarding profiles configured to route traffic through secure gateway",
                recommendation="Configure traffic forwarding profiles to route internet and M365 traffic through Global Secure Access for AI security monitoring: 1) Enable M365 traffic forwarding to inspect Copilot API calls and detect anomalous AI usage patterns, 2) Enable internet traffic forwarding to monitor third-party AI tool access (ChatGPT, Claude, etc), 3) Deploy Global Secure Access client to endpoints or configure remote network connectivity, 4) Review traffic logs weekly for shadow AI detection and unusual data exfiltration patterns. Without traffic forwarding, Global Secure Access cannot inspect or filter AI service usage. Essential for detecting compromised accounts using Copilot or employees uploading sensitive data to unauthorized AI platforms.",
                link_text="Configure Traffic Forwarding",
                link_url="https://learn.microsoft.com/entra/global-secure-access/how-to-manage-forwarding-profiles",
                priority="Medium",
                status=status
            ))
        
        # Traffic forwarding configured - show what's enabled
        else:
            forwarding_details = []
            if m365_forwarding:
                forwarding_details.append("M365 traffic")
            if internet_forwarding:
                forwarding_details.append("internet traffic")
            
            if forwarding_details:
                observations.append(new_recommendation(
                    service="Entra",
                    feature=feature_name,
                    observation=f"Traffic forwarding active: {' and '.join(forwarding_details)} routed through secure gateway for AI security monitoring",
                    recommendation="",
                    link_text="Monitor AI Traffic",
                    link_url="https://learn.microsoft.com/entra/global-secure-access/how-to-view-traffic-logs",
                    status=status
                ))
    
    return observations

