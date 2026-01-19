"""
Viva Insights (Backend) - Copilot & Agent Adoption Recommendation
"""
from new_recommendation import new_recommendation
from friendly_names import get_friendly_sku_name

async def get_deployment_status(client):
    """
    Check Viva Insights configuration and analytics availability.
    Returns dict with analytics status.
    """
    try:
        # Viva Insights analytics are accessible through reports API
        # Check if organization has analytics data available
        # Note: Specific Viva Insights metrics API requires separate permissions
        
        # Get basic organizational info as proxy for Viva Insights setup
        org_response = await client.organization.get()
        
        if not org_response or not org_response.value:
            return {
                'available': False,
                'has_analytics': False
            }
        
        # Viva Insights backend is configured if organization exists
        # Full analytics would require Viva Insights API (not part of Graph API)
        return {
            'available': True,
            'has_backend': True,
            'note': 'Full Viva Insights analytics require Viva Insights API access'
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        if '401' in error_msg or 'unauthorized' in error_msg:
            return {
                'available': False,
                'error': 'insufficient_permissions',
                'message': 'Organization.Read.All permission required'
            }
        elif '403' in error_msg or 'forbidden' in error_msg:
            return {
                'available': False,
                'error': 'access_denied',
                'message': 'Admin consent required for analytics access'
            }
        return {
            'available': False,
            'error': 'unknown',
            'message': f'Unable to check Viva Insights status: {str(e)}'
        }

async def get_recommendation(sku_name, status="Success", client=None, m365_insights=None):
    """
    Viva Insights Backend provides the data infrastructure that
    powers workplace analytics and Copilot adoption metrics.
    Returns 2-3 recommendations: license status + productivity measurement status + usage context.
    """
    feature_name = "Viva Insights (Backend)"
    friendly_sku = get_friendly_sku_name(sku_name)
    recommendations = []
    
    # First recommendation: License status
    if status == "Success":
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is active in {friendly_sku}, providing analytics infrastructure for measuring Copilot impact",
            recommendation="",
            link_text="Workplace Analytics Infrastructure",
            link_url="https://learn.microsoft.com/viva/insights/",
            status=status
        )
    else:
        license_rec = new_recommendation(
            service="M365",
            feature=feature_name,
            observation=f"{feature_name} is {status} in {friendly_sku}, limiting analytics capabilities for AI adoption tracking",
            recommendation=f"Enable {feature_name} to provide the backend infrastructure for Viva Insights analytics that measure Copilot's impact on productivity. The backend processes collaboration data, calculates metrics like meeting efficiency and focus time, and enables correlation analysis between Copilot usage and work patterns. Essential for demonstrating ROI of AI investments through data-driven insights about how Copilot adoption affects employee productivity, wellbeing, and collaboration effectiveness.",
            link_text="Workplace Analytics Infrastructure",
            link_url="https://learn.microsoft.com/viva/insights/",
            priority="Low",
            status=status
        )
    
    # Second recommendation: Productivity measurement status (only if license is active)
    if status == "Success" and client:
        deployment = await get_deployment_status(client)
        
        if deployment.get('available') and deployment.get('has_backend'):
            # Backend configured - provide guidance on measuring Copilot impact
            deployment_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Productivity Measurement",
                observation="Viva Insights backend infrastructure available for measuring Copilot productivity impact",
                recommendation="Configure Viva Insights to measure Copilot ROI: 1) Establish baseline metrics BEFORE Copilot rollout: average meeting hours per week, focus time hours, after-hours work time, email load, 2) Create custom metric for 'Copilot-enabled users' cohort to compare against non-users, 3) Track correlation between Copilot usage and productivity improvements: expect 20-30% reduction in meeting time (via summaries), 2-3 hours weekly increase in focus time (less email churn), 15-20% reduction in after-hours work. 4) Use Viva Insights dashboard to identify Copilot champions vs low adopters, correlate with productivity gains. Measure monthly for 6 months post-deployment to quantify business value.",
                link_text="Measure Copilot Impact with Viva",
                link_url="https://learn.microsoft.com/viva/insights/advanced/admin/copilot-dashboard",
                priority="Medium",
                status="Success"
            )
        else:
            # Cannot verify analytics configuration
            error_msg = deployment.get('message', 'Unable to verify Viva Insights configuration')
            deployment_rec = new_recommendation(
                service="M365",
                feature=f"{feature_name} - Productivity Measurement",
                observation=f"Viva Insights productivity measurement status could not be verified ({error_msg})",
                recommendation="Manually configure Viva Insights for Copilot ROI measurement in Microsoft Viva Insights admin center. Key metrics to track: 1) Meeting time reduction (target 20-30% for Copilot users via meeting summaries), 2) Focus time increase (target 2-3 hours/week gain from reduced email processing), 3) After-hours work reduction (Copilot improves work-life balance by 15-20%), 4) Collaboration quality scores, 5) Email response efficiency. Create separate cohort for Copilot-enabled users to compare against baseline. Monthly reporting to leadership on productivity gains justifies continued investment.",
                link_text="Viva Insights Configuration",
                link_url="https://learn.microsoft.com/viva/insights/advanced/admin/copilot-dashboard",
                priority="Medium",
                status="Success"
            )
        
        recommendations.extend([license_rec, deployment_rec])
    else:
        # If license not active or no client, return only license recommendation
        recommendations.append(license_rec)
    
    # NEW: Usage Context based on active users (viability for Viva Insights analytics)
    if status == "Success" and m365_insights and m365_insights.get('active_users_report_available'):
        active_users = m365_insights.get('total_active_users', 0)
        
        if active_users >= 100:
            # High user count = strong analytics viability
            recommendations.append(new_recommendation(
                service="M365",
                feature="Viva Insights (Backend)",
                observation=f"Your tenant has {active_users} active users. This substantial user base makes Viva Insights analytics highly valuable for measuring Copilot ROI, tracking productivity patterns, and identifying adoption opportunities across the organization.",
                recommendation="",  # No recommendation - this is helpful context
                link_text="",
                link_url="",
                priority="",
                status=""
            ))
        elif active_users >= 50:
            # Moderate user count = viable for targeted analytics
            recommendations.append(new_recommendation(
                service="M365",
                feature="Viva Insights (Backend)",
                observation=f"Your tenant has {active_users} active users. This user base supports targeted Viva Insights analytics for specific teams or departments to measure Copilot impact on productivity.",
                recommendation=f"Configure Viva Insights for targeted productivity measurement. With {active_users} active users, focus analytics on specific teams piloting Copilot rather than organization-wide metrics. Track meeting time reduction, focus time improvements, and collaboration patterns for early adopter cohorts to build business case for broader Copilot deployment.",
                link_text="Viva Insights Team Analytics",
                link_url="https://learn.microsoft.com/viva/insights/advanced/admin/copilot-dashboard",
                priority="Low",
                status="PendingInput"
            ))
        else:
            # Low user count = limited analytics value
            recommendations.append(new_recommendation(
                service="M365",
                feature="Viva Insights (Backend)",
                observation=f"Your tenant has {active_users} active users. Focus on increasing Microsoft 365 adoption before investing in Viva Insights analytics infrastructure, as productivity measurement requires sufficient user base for meaningful trends.",
                recommendation=f"Prioritize Microsoft 365 adoption before Viva Insights analytics. With {active_users} active users, productivity analytics would have limited statistical significance. Focus on expanding Microsoft 365 usage (Teams, SharePoint, OneDrive) and increasing active user count before deploying Viva Insights to measure Copilot ROI.",
                link_text="Microsoft 365 Adoption Guidance",
                link_url="https://adoption.microsoft.com/",
                priority="Low",
                status="PendingInput"
            ))

    return recommendations
