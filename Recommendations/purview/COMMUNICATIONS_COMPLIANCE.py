"""
Communication Compliance - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Communication Compliance monitors Copilot interactions for policy violations,
    inappropriate AI usage, and sensitive data sharing through prompts.
    """
    feature_name = "Communication Compliance"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, monitoring Copilot conversations for compliance risks",
            recommendation="",
            link_text="Monitor AI Conversations for Compliance",
            link_url="https://learn.microsoft.com/purview/communication-compliance",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, leaving Copilot usage unmonitored for compliance violations",
            recommendation=f"Enable {feature_name} to monitor M365 Copilot conversations for regulatory violations, inappropriate use cases, and sensitive data exposure through prompts. Detect when employees attempt to bypass information barriers through AI, share confidential information in Copilot chats, or use AI assistants in ways that violate organizational policies. Essential for regulated industries adopting Copilot.",
            link_text="Monitor AI Conversations for Compliance",
            link_url="https://learn.microsoft.com/purview/communication-compliance",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'comm_compliance'):
        comm_data = purview_client.comm_compliance
        
        # Generate recommendation whether data is available or not (0 count = not configured)
        total_policies = comm_data.get('total_policies', 0)
        policies = comm_data.get('policies', [])
        
        if total_policies > 0:
            enabled_policies = [p for p in policies if p.get('Enabled') == True]
            policy_names = ', '.join([p.get('Name', 'Unnamed') for p in policies[:2]])
            if len(policies) > 2:
                policy_names += f" (+{len(policies)-2} more)"
            
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Policy Status",
                    observation=f"{total_policies} Communication Compliance policies configured ({len(enabled_policies)} enabled): {policy_names}",
                    recommendation=f"Verify policies monitor Copilot interactions: 1) Inappropriate language in Copilot chats (harassment, profanity), 2) Sharing confidential data through AI prompts, 3) Using Copilot to generate prohibited content (legal advice, medical diagnosis), 4) Attempting to bypass information barriers via AI. Review in Purview > Communication compliance. Currently {len(enabled_policies)}/{total_policies} policies active.",
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
                    observation="Communication Compliance license active but NO policies configured - Copilot usage unmonitored",
                    recommendation="Deploy Communication Compliance policies to monitor Copilot usage: 1) Create policy to detect confidential data keywords in prompts (SSN, credit cards, medical records), 2) Monitor for inappropriate language in AI conversations, 3) Detect attempts to use Copilot for prohibited purposes (legal/medical advice), 4) Flag cross-barrier communication attempts via AI. Without policies, employees can misuse Copilot without detection. Configure in Purview > Communication compliance.",
                    link_text="Create Communication Compliance Policies",
                    link_url="https://learn.microsoft.com/purview/communication-compliance-configure",
                    priority="High",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
