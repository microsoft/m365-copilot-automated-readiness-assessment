"""
Insider Risk Management - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Insider Risk Management detects when users abuse Copilot to exfiltrate
    data at scale or use AI to access information beyond their normal scope.
    """
    feature_name = "Insider Risk Management"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, monitoring for data exfiltration risks through Copilot usage",
            recommendation="",
            link_text="Detect Copilot Misuse with Insider Risk",
            link_url="https://learn.microsoft.com/purview/insider-risk-management",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing detection of AI-assisted data theft",
            recommendation=f"Enable {feature_name} to identify malicious use of Copilot for data gathering. Detect when departing employees use Copilot to quickly aggregate competitive intelligence, customer lists, or intellectual property. Identify unusual patterns like sudden spikes in Copilot queries about sensitive projects, accessing data outside normal work scope through AI, or using Copilot to batch-download content before resignation. Insider Risk correlates Copilot usage with other risky behaviors to catch sophisticated data theft that AI makes easier and faster.",
            link_text="Detect Copilot Misuse with Insider Risk",
            link_url="https://learn.microsoft.com/purview/insider-risk-management",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'insider_risk'):
        irm_data = purview_client.insider_risk
        
        # Generate recommendation whether data is available or not (0 count = not configured)
        total_policies = irm_data.get('total_policies', 0)
        policies = irm_data.get('policies', [])
        
        if total_policies > 0:
            enabled_policies = [p for p in policies if p.get('Enabled') == True]
            policy_names = ', '.join([p.get('Name', 'Unnamed') for p in policies[:2]])
            if len(policies) > 2:
                policy_names += f" (+{len(policies)-2} more)"
            
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} (Base) - Policy Status",
                    observation=f"{total_policies} Insider Risk policies configured ({len(enabled_policies)} enabled): {policy_names}",
                    recommendation=f"Verify policies detect Copilot-specific risks: 1) Unusual volume of Copilot queries about sensitive projects (data harvesting), 2) Accessing content outside normal scope via AI assistance, 3) Copying large amounts of Copilot-retrieved data to external storage, 4) Copilot usage patterns that correlate with resignation/termination indicators. Review in Purview > Insider risk management. Currently {len(enabled_policies)}/{total_policies} policies active.",
                    link_text="Insider Risk Policies",
                    link_url="https://learn.microsoft.com/purview/insider-risk-management-policies",
                    priority="Medium" if len(enabled_policies) > 0 else "High",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
        else:
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} (Base) - Policy Status",
                    observation="Insider Risk Management license active but NO policies configured - AI-assisted data theft undetected",
                    recommendation="Deploy Insider Risk policies to detect malicious Copilot usage. Create policies for: 1) Data exfiltration by departing employees (spike in Copilot queries + downloads before resignation), 2) Unauthorized data access (using Copilot to explore sensitive areas beyond normal scope), 3) Intellectual property theft (aggregating trade secrets via AI), 4) Competitor intelligence gathering (suspicious Copilot research patterns). Copilot makes data theft easier - Insider Risk detects the patterns. Configure in Purview > Insider risk management.",
                    link_text="Create Insider Risk Policies",
                    link_url="https://learn.microsoft.com/purview/insider-risk-management-configure",
                    priority="High",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
