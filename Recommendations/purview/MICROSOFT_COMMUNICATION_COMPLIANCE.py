"""
Communication Compliance - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Communication Compliance monitors messages for policy violations
    including inappropriate use of Copilot and agent interactions.
    """
    feature_name = "Communication Compliance (Microsoft)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, monitoring Copilot interactions and agent conversations for policy compliance",
            recommendation="",
            link_text="Monitor AI Conversations for Compliance",
            link_url="https://learn.microsoft.com/purview/communication-compliance",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, missing detection of policy violations in AI interactions",
            recommendation=f"Enable {feature_name} to detect inappropriate use of Copilot, including attempts to manipulate the AI, generate harmful content, or extract sensitive information against policy. Monitor agent conversations for data exposure, track Copilot prompts that violate compliance rules, and identify users trying to bypass security through AI. Detect patterns like asking Copilot to generate fraudulent communications, using agents to circumvent approval processes, or prompting AI to reveal confidential information. Critical for regulated industries ensuring AI interactions meet compliance standards.",
            link_text="Monitor AI Conversations for Compliance",
            link_url="https://learn.microsoft.com/purview/communication-compliance",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'comm_compliance'):
        comm_comp_data = purview_client.comm_compliance
        
        # Generate recommendation whether data is available or not (0 count = not configured)
        total_policies = comm_comp_data.get('total_policies', 0)
        policies = comm_comp_data.get('policies', [])
        
        if total_policies > 0:
            enabled_policies = [p for p in policies if p.get('Enabled') == True]
            policy_names = ', '.join([p.get('Name', 'Unnamed') for p in policies[:2]])
            if len(policies) > 2:
                policy_names += f" (+{len(policies)-2} more)"
            
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Policy Status",
                    observation=f"{total_policies} Communication Compliance policies configured ({len(enabled_policies)} enabled): {policy_names}",
                    recommendation=f"Verify policies monitor Copilot-specific scenarios: 1) Inappropriate prompts (requesting harmful/fraudulent content), 2) Data exposure attempts (asking Copilot to reveal confidential info), 3) Compliance violations (using AI to draft non-compliant communications), 4) Jailbreak attempts (trying to bypass AI safety controls). Review policies in Purview portal to ensure coverage for AI interactions. Currently {len(enabled_policies)}/{total_policies} policies active.",
                    link_text="Communication Compliance Policies",
                    link_url="https://learn.microsoft.com/purview/communication-compliance-policies",
                    priority="Medium" if len(enabled_policies) > 0 else "High",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
        else:
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Policy Status",
                    observation="Communication Compliance license active but NO policies configured - AI interactions are unmonitored",
                    recommendation="Deploy Communication Compliance policies to monitor Copilot usage for policy violations. Create policies to detect: 1) Users asking Copilot to generate fraudulent/deceptive content, 2) Attempts to extract confidential data through clever prompts, 3) Using AI to draft communications that violate regulatory requirements, 4) Jailbreak attempts or prompt injection attacks. Essential for maintaining compliance as AI becomes primary communication tool. Configure in Purview > Communication compliance.",
                    link_text="Create Communication Compliance Policies",
                    link_url="https://learn.microsoft.com/purview/communication-compliance-policies",
                    priority="High",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
