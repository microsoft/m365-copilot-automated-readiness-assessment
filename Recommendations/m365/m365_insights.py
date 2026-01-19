"""
M365 Insights - Pre-computed usage & deployment metrics from M365 client
Similar to entra_insights and defender_insights patterns.

This module provides helper functions to generate observation text,
recommendations, and parsed metrics from Graph API usage reports.

All CSV reports are parsed ONCE during client initialization (not in concurrent feature processing).
Feature files get pre-computed metrics via simple dict access - no parsing overhead.
"""

# ============================================================================
# OBSERVATION HELPERS - Generate text for deployment status
# ============================================================================

def get_sites_observation(m365_insights):
    """
    Generate SharePoint sites observation text.
    
    Args:
        m365_insights: dict from extract_m365_insights_from_client()
    
    Returns:
        str: Observation text for sites deployment, or empty string if no data
    """
    if not m365_insights or not m365_insights.get('available'):
        return ""
    
    total_sites = m365_insights.get('total_sites', 0)
    
    if total_sites == 0:
        return "No SharePoint sites detected (Sites.Read.All permission may be missing)"
    elif total_sites < 5:
        return f"{total_sites} SharePoint sites deployed (limited content available for Copilot)"
    elif total_sites < 20:
        return f"{total_sites} SharePoint sites deployed (moderate content foundation for Copilot)"
    else:
        return f"{total_sites} SharePoint sites deployed (strong content foundation for Copilot)"


def get_sites_recommendation(m365_insights):
    """
    Generate SharePoint sites recommendation text.
    
    Args:
        m365_insights: dict from extract_m365_insights_from_client()
    
    Returns:
        str: Recommendation text, or empty string if no action needed
    """
    if not m365_insights or not m365_insights.get('available'):
        return ""
    
    total_sites = m365_insights.get('total_sites', 0)
    
    if total_sites == 0:
        return "Ensure Sites.Read.All permission is granted to assess SharePoint deployment. SharePoint provides the organizational knowledge base that Copilot uses to answer questions and generate insights."
    elif total_sites < 5:
        return "Create team sites for key departments and projects. Copilot's effectiveness depends on having organizational content in SharePoint - policies, procedures, project documentation, and collaborative workspaces. Aim for at least 10-15 active sites to provide meaningful context for AI responses."
    elif total_sites < 20:
        return "Expand SharePoint site deployment to cover more teams and business processes. More content diversity improves Copilot's ability to synthesize cross-functional insights and answer complex business questions."
    
    return ""  # Sufficient sites deployed


def get_users_observation(m365_insights):
    """
    Generate user licensing observation text.
    
    Args:
        m365_insights: dict from extract_m365_insights_from_client()
    
    Returns:
        str: Observation text for user counts and Copilot adoption
    """
    if not m365_insights or not m365_insights.get('available'):
        return ""
    
    total_users = m365_insights.get('total_users', 0)
    copilot_licensed = m365_insights.get('copilot_licensed_users', 0)
    adoption_rate = m365_insights.get('copilot_adoption_rate', 0)
    
    if total_users == 0:
        return "User data unavailable (User.Read.All permission may be missing)"
    
    observation_parts = [f"{total_users} total users"]
    
    if copilot_licensed > 0:
        observation_parts.append(f"{copilot_licensed} with Copilot licenses ({adoption_rate}% adoption)")
    else:
        observation_parts.append("no Copilot licenses assigned yet")
    
    return ", ".join(observation_parts)


def get_copilot_adoption_recommendation(m365_insights):
    """
    Generate Copilot license adoption recommendation.
    
    Args:
        m365_insights: dict from extract_m365_insights_from_client()
    
    Returns:
        str: Recommendation for Copilot license rollout strategy
    """
    if not m365_insights or not m365_insights.get('available'):
        return ""
    
    total_users = m365_insights.get('total_users', 0)
    copilot_licensed = m365_insights.get('copilot_licensed_users', 0)
    adoption_rate = m365_insights.get('copilot_adoption_rate', 0)
    
    if total_users == 0:
        return ""
    
    if copilot_licensed == 0:
        return "Start Copilot pilot with 10-20 power users from different departments to validate value before broad rollout. Focus on users who create lots of content, attend many meetings, or need to synthesize information from multiple sources."
    elif adoption_rate < 10:
        return f"Expand Copilot deployment beyond current {copilot_licensed} users. Pilot phase is validating value - gather feedback, identify use cases with highest ROI, then scale to similar user profiles. Target 20-30% adoption within 6 months for meaningful organizational impact."
    elif adoption_rate < 30:
        return f"Continue measured rollout from current {adoption_rate}% adoption. Monitor usage metrics, identify champions in each business unit, and create adoption playbooks based on successful use cases. Aim for 50% adoption within 12 months."
    elif adoption_rate < 60:
        return f"Strong adoption at {adoption_rate}%. Focus on enabling remaining users - identify barriers (training needs, workflow integration, data gaps), address skepticism with ROI data from early adopters, and consider mandating for high-value scenarios."
    
    return ""  # High adoption already achieved


def get_reports_observation(m365_insights):
    """
    Generate observation about available usage reports.
    
    Args:
        m365_insights: dict from extract_m365_insights_from_client()
    
    Returns:
        str: Summary of what usage data is available for analysis
    """
    if not m365_insights or not m365_insights.get('available'):
        return ""
    
    available_reports = []
    
    if m365_insights.get('email_report_available'):
        available_reports.append('Email activity')
    if m365_insights.get('teams_report_available'):
        available_reports.append('Teams activity')
    if m365_insights.get('sharepoint_report_available'):
        available_reports.append('SharePoint usage')
    if m365_insights.get('onedrive_report_available'):
        available_reports.append('OneDrive usage')
    if m365_insights.get('activations_report_available'):
        available_reports.append('Office activations')
    if m365_insights.get('active_users_report_available'):
        available_reports.append('Active users')
    
    if not available_reports:
        return "Usage reports unavailable (Reports.Read.All permission may be missing)"
    
    report_list = ', '.join(available_reports)
    return f"Usage reports available: {report_list} (30-day baseline for Copilot impact measurement)"


def get_reports_recommendation(m365_insights):
    """
    Generate recommendation about establishing usage baselines.
    
    Args:
        m365_insights: dict from extract_m365_insights_from_client()
    
    Returns:
        str: Guidance on using usage reports for Copilot ROI measurement
    """
    if not m365_insights or not m365_insights.get('available'):
        return ""
    
    has_teams = m365_insights.get('teams_report_available', False)
    has_email = m365_insights.get('email_report_available', False)
    has_sharepoint = m365_insights.get('sharepoint_report_available', False)
    
    missing_reports = []
    if not has_teams:
        missing_reports.append('Teams')
    if not has_email:
        missing_reports.append('Email')
    if not has_sharepoint:
        missing_reports.append('SharePoint')
    
    if missing_reports:
        return f"Ensure Reports.Read.All permission is granted to access {', '.join(missing_reports)} usage data. Baseline metrics are critical for measuring Copilot's impact on productivity - meeting time reduction, email volume changes, content collaboration patterns."
    
    # If all reports available, provide ROI guidance
    return "Establish baseline metrics before Copilot rollout: avg meeting duration, emails sent per user, documents created per week, time in collaborative work. After deployment, measure impact: 20-30% reduction in meeting time (via summaries), 15% reduction in email volume (via chat recaps), 25% increase in content reuse. Use these reports monthly to quantify Copilot ROI."


def has_sufficient_data_for_observations(m365_insights):
    """
    Check if M365 client has enough data to provide meaningful observations.
    
    Args:
        m365_insights: dict from extract_m365_insights_from_client()
    
    Returns:
        bool: True if at least basic data (sites OR users OR reports) is available
    """
    if not m365_insights or not m365_insights.get('available'):
        return False
    
    has_sites = m365_insights.get('total_sites', 0) > 0
    has_users = m365_insights.get('total_users', 0) > 0
    has_any_report = (
        m365_insights.get('email_report_available', False) or
        m365_insights.get('teams_report_available', False) or
        m365_insights.get('sharepoint_report_available', False) or
        m365_insights.get('onedrive_report_available', False)
    )
    
    return has_sites or has_users or has_any_report


def get_missing_permissions_warning(m365_insights):
    """
    Get a warning message if critical permissions are missing.
    
    Args:
        m365_insights: dict from extract_m365_insights_from_client()
    
    Returns:
        str: Warning message or empty string
    """
    if not m365_insights:
        return ""
    
    missing = m365_insights.get('missing_permissions', [])
    
    if not missing:
        return ""
    
    if len(missing) == 1:
        return f"Missing permission: {missing[0]} - some deployment observations unavailable"
    else:
        return f"Missing permissions: {', '.join(missing)} - limited deployment visibility"


# ============================================================================
# METRIC ACCESS - Pre-parsed values from CSV reports (no parsing needed!)
# ============================================================================

def get_site_count(m365_insights):
    """Get total SharePoint sites deployed"""
    return m365_insights.get('total_sites', 0) if m365_insights else 0

def get_site_names(m365_insights):
    """Get list of SharePoint site display names"""
    return m365_insights.get('site_names', []) if m365_insights else []

def get_total_users(m365_insights):
    """Get total user count (sampled if >999)"""
    return m365_insights.get('total_users', 0) if m365_insights else 0

def get_copilot_licensed_count(m365_insights):
    """Get number of users with Copilot licenses"""
    return m365_insights.get('copilot_licensed_users', 0) if m365_insights else 0

def get_copilot_adoption_percentage(m365_insights):
    """Get Copilot license adoption rate as percentage"""
    return m365_insights.get('copilot_adoption_rate', 0) if m365_insights else 0

def is_user_data_sampled(m365_insights):
    """Check if user data is sampled (>999 users - only first 999 retrieved)"""
    return m365_insights.get('user_data_sampled', False) if m365_insights else False

# Teams Metrics
def get_teams_active_users(m365_insights):
    """Get number of Teams active users in last 30 days"""
    return m365_insights.get('teams_active_users', 0) if m365_insights else 0

def get_teams_total_meetings(m365_insights):
    """Get total Teams meetings in last 30 days"""
    return m365_insights.get('teams_total_meetings', 0) if m365_insights else 0

def get_teams_avg_meetings_per_user(m365_insights):
    """Get average meetings per user"""
    return m365_insights.get('teams_avg_meetings_per_user', 0) if m365_insights else 0

# Email Metrics
def get_email_active_users(m365_insights):
    """Get number of email active users in last 30 days"""
    return m365_insights.get('email_active_users', 0) if m365_insights else 0

def get_email_avg_sent_per_user(m365_insights):
    """Get average emails sent per user"""
    return m365_insights.get('email_avg_sent_per_user', 0) if m365_insights else 0

# SharePoint Metrics
def get_sharepoint_active_sites(m365_insights):
    """Get number of active SharePoint sites (with page views)"""
    return m365_insights.get('sharepoint_active_sites', 0) if m365_insights else 0

def get_sharepoint_activity_rate(m365_insights):
    """Get SharePoint site activity rate as percentage"""
    return m365_insights.get('sharepoint_activity_rate', 0) if m365_insights else 0

# OneDrive Metrics
def get_onedrive_adoption_rate(m365_insights):
    """Get OneDrive adoption rate as percentage"""
    return m365_insights.get('onedrive_adoption_rate', 0) if m365_insights else 0

def get_onedrive_active_accounts(m365_insights):
    """Get number of active OneDrive accounts"""
    return m365_insights.get('onedrive_active_accounts', 0) if m365_insights else 0
