"""
Communication DLP - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """
    Check DLP policy deployment via Graph API (fallback - checks labels as proxy).
    Returns dict with policy details.
    """
    try:
        # Get information protection labels from Graph API as proxy for DLP
        # Note: Graph API doesn't directly expose DLP policies
        policies_response = await client.information_protection.policy.labels.get()
        
        if not policies_response or not policies_response.value:
            return {
                'available': False,
                'total_labels': 0,
                'has_protection_framework': False
            }
        
        total_labels = len(policies_response.value)
        
        return {
            'available': True,
            'total_labels': total_labels,
            'has_protection_framework': total_labels > 0
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        if '401' in error_msg or 'unauthorized' in error_msg:
            return {
                'available': False,
                'error': 'insufficient_permissions',
                'message': 'InformationProtectionPolicy.Read permission required'
            }
        elif '403' in error_msg or 'forbidden' in error_msg:
            return {
                'available': False,
                'error': 'access_denied',
                'message': 'Admin consent required for InformationProtectionPolicy.Read'
            }
        return {
            'available': False,
            'error': 'unknown',
            'message': f'Unable to check DLP policies: {str(e)}'
        }

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Communication DLP prevents users from sharing sensitive information
    extracted by Copilot through Teams chats and other messaging platforms.
    Returns 2 recommendations: license status + DLP policy coverage status.
    """
    feature_name = "Communication DLP"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, preventing data leaks through AI-assisted communications",
            recommendation="",
            link_text="DLP for Copilot Communications",
            link_url="https://learn.microsoft.com/purview/dlp-microsoft-teams",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, allowing uncontrolled sharing of Copilot-retrieved sensitive data",
            recommendation=f"Enable {feature_name} to prevent users from pasting Copilot-generated content containing PII, financial data, or trade secrets into Teams chats, emails, or collaboration platforms. When Copilot retrieves sensitive information and presents it to users, Communication DLP blocks inappropriate sharing while allowing legitimate work. This addresses the unique risk that Copilot makes it trivially easy to gather and redistribute sensitive data that would traditionally require manual searching and compilation.",
            link_text="DLP for Copilot Communications",
            link_url="https://learn.microsoft.com/purview/dlp-microsoft-teams",
            priority="High",
            status=status
        )
    
    # Collect all deployment recommendations
    deployment_recs = []
    
    # Second recommendation: DLP policy coverage via Graph API (labels as proxy)
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        
        if deployment.get('available') and deployment.get('has_protection_framework'):
            total_labels = deployment.get('total_labels', 0)
            # Good - has information protection framework for DLP
            graph_rec = new_recommendation(
                service="Purview",
                feature=f"{feature_name} - Label Coverage",
                observation=f"Information protection framework active with {total_labels} sensitivity labels, supporting DLP policy enforcement for Copilot outputs",
                recommendation="Verify DLP policies in Microsoft Purview compliance portal cover Copilot scenarios: 1) Block sharing of 'Confidential' or 'Highly Confidential' labeled content in Teams/email, 2) Detect PII (SSN, credit cards, patient records) in Copilot responses, 3) Alert when sensitive data is copied from Copilot to external apps, 4) Prevent Copilot-generated summaries containing financial data from leaving org. Test policies with Copilot: ask it to summarize confidential docs, try sharing output externally. Ensure DLP blocks inappropriate sharing while allowing legitimate work.",
                link_text="DLP for Copilot Best Practices",
                link_url="https://learn.microsoft.com/purview/dlp-microsoft-teams",
                priority="Medium",
                status="Success"
            )
            deployment_recs.append(graph_rec)
    
    # Third recommendation: DLP policy coverage via PowerShell cache (actual policies)
    if status == "Success" and purview_client and hasattr(purview_client, 'dlp_policies'):
        # Use cached data from PowerShell wrapper
        dlp_data = purview_client.dlp_policies
        
        if dlp_data.get('available'):
            total_policies = dlp_data.get('total_policies', 0)
            policies = dlp_data.get('policies', [])
            
            # Analyze policies for Copilot coverage
            enabled_policies = [p for p in policies if p.get('Enabled') == True]
            teams_policies = [p for p in policies if p.get('ExchangeLocation') or 'All' in str(p.get('ExchangeLocation', []))]
            
            if total_policies > 0:
                # Good - has DLP policies deployed
                policy_names = ', '.join([p.get('Name', 'Unnamed') for p in policies[:3]])
                if len(policies) > 3:
                    policy_names += f" (+{len(policies)-3} more)"
                
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Policy Coverage",
                    observation=f"{total_policies} DLP policies configured ({len(enabled_policies)} enabled): {policy_names}. Policies protect Copilot outputs in Teams, Exchange, SharePoint.",
                    recommendation=f"Verify DLP policies cover Copilot-specific scenarios: 1) Test by asking Copilot to summarize confidential documents - attempt sharing in Teams (should block), 2) Check policies detect PII patterns in Copilot responses (SSN, credit cards), 3) Ensure policies cover Exchange (Copilot email drafts) and SharePoint (Copilot-generated docs), 4) Review policy modes - ensure critical policies are in 'Enforce' not 'Test' mode. Currently: {len(enabled_policies)}/{total_policies} policies enabled.",
                    link_text="DLP for Copilot Best Practices",
                    link_url="https://learn.microsoft.com/purview/dlp-microsoft-teams",
                    priority="Low" if len(enabled_policies) >= 2 else "Medium",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                # No DLP policies - critical gap
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Policy Coverage",
                    observation="Communication DLP license active but ZERO DLP policies configured - Copilot outputs are UNPROTECTED",
                    recommendation="Deploy DLP policies NOW before scaling Copilot adoption. Without policies, users can freely share Copilot-retrieved sensitive data externally. Required policies: 1) Block sharing documents labeled 'Highly Confidential' in Teams/email, 2) Detect PII (SSN, credit cards, patient data) in Copilot responses, 3) Alert on financial data in Copilot summaries, 4) Prevent copying trade secrets from Copilot to external apps. Copilot makes it trivial to aggregate sensitive data - DLP prevents inadvertent leaks. Configure policies in Purview compliance portal > Data loss prevention.",
                    link_text="Configure DLP for Copilot",
                    link_url="https://learn.microsoft.com/purview/dlp-learn-about-dlp",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
        else:
            # No cached data - PowerShell wrapper not run
            deployment_rec = new_recommendation(
                service="Purview",
                feature=f"{feature_name} - Policy Coverage",
                observation="INFO: DLP policy deployment status unavailable - run with PowerShell wrapper for detailed policy analysis",
                recommendation="To get deployment-specific DLP recommendations, run: .\\collect_purview_data.ps1 instead of 'python main.py'. The script collects DLP policy data via Connect-IPPSSession, then runs the assessment. This provides detailed analysis of configured policies, enabled/disabled status, and coverage gaps for Copilot scenarios.",
                link_text="DLP Policy Guide",
                link_url="https://learn.microsoft.com/purview/dlp-learn-about-dlp",
                priority="Low",
                status="Success"
            )
            deployment_recs.append(deployment_rec)
    
    # Return all recommendations: license + any deployment recommendations
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    # If no deployment data available, return only license recommendation
    return [license_rec]
