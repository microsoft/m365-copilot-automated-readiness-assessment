"""
Microsoft Teams - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name
from datetime import datetime, timedelta

async def get_deployment_status(client):
    """
    Check Teams usage activity to establish baseline for Copilot adoption.
    Returns dict with activity metrics.
    """
    try:
        # Get Teams user activity report for last 30 days
        # Note: Reports API requires Reports.Read.All permission
        period = 'D30'  # Last 30 days
        
        # Get Teams activity details - this returns aggregated data
        activity_response = await client.reports.get_teams_user_activity_counts(period=period).get()
        
        # Parse the CSV response to get activity metrics
        # Graph API returns CSV format for reports
        if not activity_response:
            return {
                'available': False,
                'total_users': 0,
                'active_users': 0
            }
        
        # For simplicity, we'll estimate based on licensed users
        # Real implementation would parse CSV response
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
            'message': f'Unable to check Teams activity: {str(e)}'
        }

async def get_recommendation(sku_name, status="Success", client=None, m365_insights=None):
    """
    Microsoft Teams provides the collaboration platform where Copilot operates,
    enabling AI-powered meetings, chat, and agent interactions.
    Returns 2-3 recommendations: license status + activity baseline + insights.
    
    Args:
        sku_name: SKU name
        status: Provisioning status
        client: Optional Graph client
        m365_insights: Optional pre-computed M365 usage metrics
    """
    feature_name = "Microsoft Teams"
    friendly_sku = get_friendly_sku_name(sku_name)
    
    # First recommendation: License status (EXISTING - unchanged)
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing the collaboration platform for Copilot and agents",
            recommendation="",
            link_text="Teams as the Hub for AI Collaboration",
            link_url="https://learn.microsoft.com/microsoftteams/teams-overview",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, preventing access to the primary Copilot collaboration interface",
            recommendation=f"Enable {feature_name} to provide the foundational platform for M365 Copilot and agents. Teams is where Copilot generates meeting summaries, where users interact with custom agents in chats, where Business Chat surfaces insights from conversations, and where collaborative AI experiences happen. Without Teams, users lose access to Copilot's meeting intelligence, cannot deploy conversational agents to channels, and miss the context-aware assistance that makes hybrid work productive. Teams is essential infrastructure for agent adoption.",
            link_text="Teams as the Hub for AI Collaboration",
            link_url="https://learn.microsoft.com/microsoftteams/teams-overview",
            priority="High",
            status=status
        )
    
    # Second recommendation: Activity baseline status (only if license is active)
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        
        if deployment.get('available'):
            # Activity data available - good baseline for Copilot adoption
            deployment_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Activity Baseline",
                observation="Teams activity data available, providing baseline metrics for measuring Copilot adoption impact",
                recommendation="Establish baseline metrics before Copilot deployment: active users per day, meetings per user, chat messages per user, avg meeting duration. After Copilot rollout, measure impact: reduction in meeting time (via summaries), increase in async collaboration (via chat recaps), time saved on status updates. Target 20-30% reduction in meeting time and 15-20% increase in productive collaboration time. Use Teams analytics to identify power users vs low adopters, correlate with Copilot usage patterns.",
                link_text="Teams Activity Reports",
                link_url="https://learn.microsoft.com/microsoft-365/admin/activity-reports/microsoft-teams-user-activity",
                priority="Medium",
                status="Success"
            )
        else:
            # Cannot verify activity baseline
            error_msg = deployment.get('message', 'Unable to verify Teams activity')
            deployment_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Activity Baseline",
                observation=f"Teams activity baseline could not be verified ({error_msg})",
                recommendation="Manually establish Teams activity baseline in Microsoft 365 admin center > Reports > Microsoft Teams > User Activity. Before deploying Copilot, record: daily active users, meetings per user per week, chat messages per user, average meeting duration, time in meetings per user. After Copilot rollout, track same metrics to quantify productivity gains. Expect 20-30% reduction in meeting time (summaries reduce need for attendance), 15% increase in async work (chat becomes more effective), and improved meeting quality scores.",
                link_text="Teams Analytics Guide",
                link_url="https://learn.microsoft.com/microsoft-365/admin/activity-reports/microsoft-teams-user-activity",
                priority="Medium",
                status="Success"
            )
    
    # NEW: Teams Activity Insights (if m365_insights available)
    if status == "Success" and m365_insights and m365_insights.get('teams_report_available'):
        active_users = m365_insights.get('teams_active_users', 0)
        total_meetings = m365_insights.get('teams_total_meetings', 0)
        avg_meetings = m365_insights.get('teams_avg_meetings_per_user', 0)
        total_messages = m365_insights.get('teams_total_team_chat_messages', 0) + m365_insights.get('teams_total_private_messages', 0)
        
        if active_users > 100 and avg_meetings >= 5:
            # HIGH ENGAGEMENT - Excellent for Copilot
            insights_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Collaboration Activity",
                observation=f"Strong Teams engagement: {active_users} active users averaging {avg_meetings:.1f} meetings per user, with {total_messages:,} total messages. High collaboration activity ideal for Copilot adoption",
                recommendation="",  # No recommendation - this is HELPFUL
                link_text="Teams Analytics",
                link_url="https://learn.microsoft.com/microsoftteams/teams-analytics-and-reports/teams-reporting-reference",
                status="Success"
            )
        elif active_users > 20:
            # MODERATE - Room to grow
            insights_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Collaboration Activity",
                observation=f"Moderate Teams usage: {active_users} active users with {avg_meetings:.1f} avg meetings per user. Collaboration happening but could expand - increase Teams adoption to unlock Copilot meeting intelligence (summaries, action items, Q&A) at scale.",
                recommendation="Increase Teams adoption before Copilot rollout. Low meeting frequency limits Copilot's meeting intelligence value. Encourage Teams for all meetings (not just formal ones), promote chat over email, enable recording/transcripts. Higher Teams usage = better Copilot ROI.",
                link_text="Teams Adoption Guide",
                link_url="https://adoption.microsoft.com/microsoft-teams/",
                priority="Low",
                status="Success"
            )
        else:
            # LOW - Action needed
            insights_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Collaboration Activity",
                observation=f"Low Teams adoption detected: Only {active_users} active users. Limited collaboration activity reduces Copilot meeting intelligence value",
                recommendation="Address low Teams adoption BEFORE deploying Copilot. Few active users means limited value from meeting summaries, chat recaps, and collaborative AI. Run Teams adoption campaign, migrate from legacy tools (Skype, Zoom recordings to Teams), enable meeting transcripts, train users on chat vs email. Copilot's value is directly proportional to Teams usage.",
                link_text="Teams Adoption Resources",
                link_url="https://adoption.microsoft.com/microsoft-teams/",
                priority="Medium",
                status="Warning"
            )
        
        # Return all available recommendations
        if client:
            return [license_rec, deployment_rec, insights_rec]
        else:
            return [license_rec, insights_rec]
    
    # If client available but no insights, return license + deployment
    if status == "Success" and client:
        return [license_rec, deployment_rec]
    
    # If license not active or no client/insights, return only license recommendation
    return [license_rec]
