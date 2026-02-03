"""
Information Barriers - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Information Barriers prevent Copilot from inadvertently sharing information
    between restricted groups, essential for regulated industries and ethical walls.
    """
    feature_name = "Information Barriers"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, preventing Copilot from crossing compliance boundaries",
            recommendation="",
            link_text="Information Barriers for AI Compliance",
            link_url="https://learn.microsoft.com/purview/information-barriers",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, risking compliance violations through AI data sharing",
            recommendation=f"Enable {feature_name} to enforce ethical walls that Copilot must respect. In financial services, legal firms, and other regulated industries, certain employees cannot share information (e.g., M&A teams working on competing deals, research and trading divisions). Information Barriers ensure that when Copilot searches for content or generates responses, it only accesses data the user is permitted to see, preventing the AI from becoming a conduit for inappropriate information flow. Critical for Copilot adoption in regulated environments.",
            link_text="Information Barriers for AI Compliance",
            link_url="https://learn.microsoft.com/purview/information-barriers",
            priority="High",
            status=status
        )
    
    # Check deployment status from PowerShell data
    deployment_recs = []
    if status == "Success" and purview_client and hasattr(purview_client, 'information_barriers'):
        ib_data = purview_client.information_barriers
        
        # Generate recommendation whether data is available or not (0 count = not configured)
        total_policies = ib_data.get('total_policies', 0)
        policies = ib_data.get('policies', [])
        
        if total_policies > 0:
            active_policies = [p for p in policies if p.get('State') == 'Active']
            policy_names = ', '.join([p.get('Name', 'Unnamed') for p in policies[:2]])
            if len(policies) > 2:
                policy_names += f" (+{len(policies)-2} more)"
            
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Policy Status",
                    observation=f"{total_policies} Information Barrier policies configured ({len(active_policies)} active): {policy_names}",
                    recommendation=f"Verify barriers enforce ethical walls for Copilot: 1) Test: user in restricted group asks Copilot about prohibited project (should not retrieve), 2) Ensure segments cover all groups needing separation (M&A teams, trading desks, legal matters), 3) Validate Copilot respects barriers in search, chat, and document access, 4) Review policy application status. Currently {len(active_policies)}/{total_policies} policies active.",
                    link_text="Information Barrier Policies",
                    link_url="https://learn.microsoft.com/purview/information-barriers-policies",
                    priority="Medium" if len(active_policies) > 0 else "High",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
        else:
            deployment_rec = new_recommendation(
                    service="Purview",
                    feature=f"{feature_name} - Policy Status",
                    observation="Information Barriers license active but NO policies configured - Copilot can cross ethical walls",
                    recommendation="Deploy Information Barrier policies for Copilot compliance. Define segments and barriers: 1) M&A teams on competing deals cannot share via Copilot, 2) Research/trading divisions maintain ethical wall through AI, 3) Legal teams on opposing cases keep data separated, 4) Regulatory compliance groups in financial services. Without barriers, Copilot becomes information leak vector across restricted groups. Configure in Purview > Information barriers.",
                    link_text="Configure Information Barriers",
                    link_url="https://learn.microsoft.com/purview/information-barriers-policies",
                    priority="High",
                    status="Success"
            )
            deployment_recs.append(deployment_rec)
    
    if deployment_recs:
        return [license_rec] + deployment_recs
    
    return [license_rec]
