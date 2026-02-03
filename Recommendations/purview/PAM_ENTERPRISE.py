"""
Privileged Access Management - Copilot & Agent Adoption Recommendation
"""
from Core.new_recommendation import new_recommendation
from Core.friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, purview_client=None):
    """
    Privileged Access Management provides just-in-time admin access
    controls that protect sensitive operations from unauthorized AI use.
    """
    feature_name = "Privileged Access Management"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    if status == "Success":
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enforcing approval workflows for privileged operations with AI",
            recommendation="",
            link_text="Control Privileged AI Operations",
            link_url="https://learn.microsoft.com/purview/privileged-access-management/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="Purview",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, lacking just-in-time access controls for sensitive AI operations",
            recommendation=f"Enable {feature_name} to require approval for privileged administrative tasks, even when requested through conversational agents. Prevent scenarios where agents or Copilot-assisted users attempt sensitive operations (mailbox access, permission changes, data exports) without proper oversight. PAM ensures that AI-driven productivity doesn't bypass governance controls, requiring human approval for high-risk actions while allowing automation of routine tasks. Critical for maintaining security in organizations deploying autonomous agents.",
            link_text="Control Privileged AI Operations",
            link_url="https://learn.microsoft.com/purview/privileged-access-management/",
            priority="Medium",
            status=status
        )
    
    return [license_rec]
