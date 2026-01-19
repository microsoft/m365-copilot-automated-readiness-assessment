"""
Exchange Online (Plan 2) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_recommendation(sku_name, status="Success", client=None, m365_insights=None):
    """
    Generate recommendation for Exchange Online (Plan 2).
    Exchange provides email and calendar services that Copilot uses
    to draft emails, summarize threads, and manage communications intelligently.
    Returns 2 recommendations: license status + activity baseline status.
    
    Args:
        sku_name: License SKU name
        status: Provisioning status
        client: Graph API client (optional, for legacy support)
        m365_insights: Pre-computed M365 metrics (preferred)
    """
    feature_name = "Exchange Online (Plan 2)"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, enabling Copilot to assist with email management and calendar intelligence",
            recommendation="",
            link_text="Intelligent Email with Copilot",
            link_url="https://learn.microsoft.com/exchange/exchange-online",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting Copilot's email and scheduling capabilities",
            recommendation=f"Enable {feature_name} to let Copilot transform email productivity. Copilot uses Exchange to draft professional responses, summarize lengthy email threads, suggest meeting times based on calendar availability, and extract action items from conversations.",
            link_text="Intelligent Email with Copilot",
            link_url="https://learn.microsoft.com/exchange/exchange-online",
            priority="High",
            status=status
        )
    
    # Second recommendation: Activity baseline status (only if license is active)
    if status == "Success":
        # Use insights if available, otherwise fall back to legacy client approach
        if m365_insights and m365_insights.get('email_report_available'):
            active_users = m365_insights.get('email_active_users', 0)
            avg_sent = m365_insights.get('email_avg_sent_per_user', 0)
            
            deployment_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Activity Baseline",
                observation=f"Email activity data available: {active_users} active users, averaging {avg_sent} emails sent per user. Baseline established for measuring Copilot impact",
                recommendation="Track email metrics before and after Copilot: drafting time (target 30-40% reduction), email volume, response quality. Focus on high-volume roles (managers, sales, support) where Copilot saves 2-3 hours weekly.",
                link_text="Exchange Activity Reports",
                link_url="https://learn.microsoft.com/microsoft-365/admin/activity-reports/email-activity",
                priority="Low",
                status=status
            )
            return [license_rec, deployment_rec]
        elif client:
            # Legacy: fetch data directly (slower)
            deployment = await get_deployment_status(client)
            
            if deployment.get('available'):
                deployment_rec = new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Activity Baseline",
                    observation="Email activity data available, baseline established for measuring Copilot impact",
                    recommendation="Track email metrics before and after Copilot: drafting time, volume, response quality.",
                    link_text="Exchange Activity Reports",
                    link_url="https://learn.microsoft.com/microsoft-365/admin/activity-reports/email-activity",
                    priority="Low",
                    status=status
                )
                return [license_rec, deployment_rec]
            else:
                error_msg = deployment.get('message', 'No activity data available')
                deployment_rec = new_recommendation(
                    service="M365",
                    feature=f"{feature_name} - Activity Baseline",
                    observation=f"Email activity data unavailable: {error_msg}",
                    recommendation="Enable Reports.Read.All permission to access email activity reports. Baseline metrics are critical for measuring Copilot ROI.",
                    link_text="Configure Reports Permission",
                    link_url="https://learn.microsoft.com/graph/permissions-reference#reportsreadall",
                    priority="Medium",
                    status="PendingActivation"
                )
                return [license_rec, deployment_rec]
    
    return [license_rec]

async def get_deployment_status(client):
    """
    Check Exchange email activity to establish baseline for Copilot adoption.
    Returns dict with activity metrics.
    """
    try:
        # Get email activity report for last 30 days
        # Note: Reports API requires Reports.Read.All permission
        period = 'D30'  # Last 30 days
        
        # Get email activity details
        activity_response = await client.reports.get_email_activity_counts(period=period).get()
        
        # Parse the response to get activity metrics
        if not activity_response:
            return {
                'available': False,
                'has_activity_data': False
            }
        
        return {
            'available': True,
            'period': '30 days',
            'has_activity_data': True
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        if '401' in error_msg or 'unauthorized' in error_msg:
            return {
                'available': False,
                'error': 'insufficient_permissions',
                'message': 'Reports.Read.All permission required'
            }
        elif '403' in error_msg or 'forbidden' in error_msg:
            return {
                'available': False,
                'error': 'access_denied',
                'message': 'Admin consent required for Reports.Read.All'
            }
        return {
            'available': False,
            'error': 'unknown',
            'message': f'Unable to check email activity: {str(e)}'
        }
