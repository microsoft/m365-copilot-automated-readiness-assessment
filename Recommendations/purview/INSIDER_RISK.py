"""
Insider Risk Management - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Insider Risk Management detects when users abuse Copilot to exfiltrate
    data at scale or use AI to access information beyond their normal scope.
    """
    feature_name = "Insider Risk Management (Base)"
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
        insider_risk_data = purview_client.insider_risk
        
        if insider_risk_data.get('available'):
            total_policies = insider_risk_data.get('total_policies', 0)
            
            if total_policies > 0:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Active Policies",
                    observation=f"Insider Risk Management has {total_policies} active policy/policies configured - monitoring framework is deployed",
                    recommendation=f"You have {total_policies} active Insider Risk policy/policies. Ensure these policies detect Copilot-related risks: 1) Monitor for unusual spikes in Copilot queries about sensitive projects, 2) Detect users accessing data outside their normal scope via AI, 3) Identify departing employees using Copilot to aggregate intellectual property, 4) Flag patterns where Copilot is used to batch-download competitive intelligence or customer data. Review policies to ensure they correlate Copilot activity with other risk indicators (file downloads, email forwarding, unauthorized access attempts). Use Get-InsiderRiskPolicy to review configurations and ensure AI-assisted data exfiltration patterns are captured.",
                    link_text="Review Insider Risk Policies",
                    link_url="https://learn.microsoft.com/purview/insider-risk-management-policies",
                    priority="Low",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
            else:
                deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Configuration",
                    observation="Insider Risk Management license is active but NO policies are configured",
                    recommendation="Create Insider Risk policies to detect Copilot misuse BEFORE data theft occurs. Deploy policies for: 1) Data theft by departing employees - detect when users about to leave suddenly use Copilot to gather customer lists, pricing strategies, or competitive intelligence, 2) Data leaks by risky users - identify unusual Copilot access patterns combined with file exfiltration behaviors, 3) Priority user monitoring - track executives/sensitive role holders who might use AI to access confidential projects outside their authorization. Configure in Purview compliance portal > Insider risk management > Policies. Start with 'Data theft by departing users' template and customize triggers to include Copilot activity signals. Use Get-InsiderRiskPolicy to verify setup.",
                    link_text="Create Insider Risk Policies",
                    link_url="https://learn.microsoft.com/purview/insider-risk-management-configure",
                    priority="High",
                    status="Success"
                )
                deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
