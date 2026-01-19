"""
Friendly display names for Microsoft 365 SKUs and service plans.
Consolidates all display name mappings for better maintainability.
"""

# Mapping of technical SKU names to friendly names
SKU_FRIENDLY_NAMES = {
    # Microsoft 365
    'Microsoft_365_Copilot': 'Microsoft 365 Copilot',
    'Microsoft_365_E5_(no_Teams)': 'Microsoft 365 E5 (no Teams)',
    'Microsoft_365_E5': 'Microsoft 365 E5',
    'Microsoft_365_E3': 'Microsoft 365 E3',
    'Microsoft_365_Business_Premium': 'Microsoft 365 Business Premium',
    'Microsoft_365_Business_Standard': 'Microsoft 365 Business Standard',
    'Microsoft_365_Business_Basic': 'Microsoft 365 Business Basic',
    'Microsoft_365_F3': 'Microsoft 365 F3',
    'Microsoft_365_F1': 'Microsoft 365 F1',
    'Microsoft_Teams_Enterprise_New': 'Microsoft Teams Enterprise',
    'Microsoft_Teams_Premium': 'Microsoft Teams Premium',
    
    # Office 365
    'Office_365_E5': 'Office 365 E5',
    'Office_365_E3': 'Office 365 E3',
    'Office_365_E1': 'Office 365 E1',
    
    # Standalone Services
    'VIRTUAL_AGENT_USL': 'Power Virtual Agents',
    'Power_Virtual_Agents': 'Power Virtual Agents',
    'FLOW_FREE': 'Power Automate Free',
    'CCIBOTS_PRIVPREV_VIRAL': 'Copilot Studio (Viral)',
    
    # Enterprise Mobility + Security
    'EMS_E5': 'Enterprise Mobility + Security E5',
    'EMS_E3': 'Enterprise Mobility + Security E3',
    
    # Add more as needed
}

# Friendly names for service plans
SERVICE_PLAN_FRIENDLY_NAMES = {
    # Intune/Device Management
    'INTUNE_O365': 'Microsoft Intune for Office 365',
    'INTUNE_A': 'Microsoft Intune (Plan A)',
    'INTUNE_SUITE': 'Microsoft Intune Suite',
    'INTUNE_SMBIZ': 'Microsoft Intune for Small Business',
    'MFA_PREMIUM': 'Microsoft Entra ID Multi-Factor Authentication',
    
    # Azure AD / Entra ID
    'AAD_PREMIUM': 'Microsoft Entra ID P1',
    'AAD_PREMIUM_P2': 'Microsoft Entra ID P2',
    'AAD_BASIC': 'Microsoft Entra ID Basic',
    
    # Purview / Compliance
    'INFORMATION_BARRIERS': 'Information Barriers',
    'INSIDER_RISK_MANAGEMENT': 'Insider Risk Management',
    'COMMUNICATIONS_COMPLIANCE': 'Communication Compliance',
    'PURVIEW_DISCOVERY': 'Microsoft Purview eDiscovery',
    'PREMIUM_ENCRYPTION': 'Premium Encryption',
    'RECORDS_MANAGEMENT': 'Records Management',
    'INSIDER_RISK': 'Insider Risk Management (Base)',
    'INFO_GOVERNANCE': 'Information Governance',
    'MICROSOFTENDPOINTDLP': 'Microsoft Endpoint DLP',
    'DATA_INVESTIGATIONS': 'Data Investigations (Standard)',
    'COMMUNICATIONS_DLP': 'Communication DLP',
    'MICROSOFT_COMMUNICATION_COMPLIANCE': 'Communication Compliance (Microsoft)',
    'MIP_S_CLP1': 'Information Protection for Office 365 - Standard',
    'MIP_S_CLP2': 'Information Protection for Office 365 - Premium',
    'MIP_S_Exchange': 'Information Protection and Governance Analytics - Premium',
    'ContentExplorer_Standard': 'Content Explorer (Standard)',
    'Content_Explorer': 'Content Explorer (Premium)',
    'CUSTOMER_KEY': 'Customer Key',
    'CustomerLockboxA_Enterprise': 'Customer Lockbox (Enterprise A)',
    'LOCKBOX_ENTERPRISE': 'Customer Lockbox (Enterprise)',
    'M365_AUDIT_PLATFORM': 'Microsoft 365 Audit Platform',
    'M365_ADVANCED_AUDITING': 'Microsoft 365 Advanced Auditing',
    'EQUIVIO_ANALYTICS': 'eDiscovery Analytics',
    'ML_CLASSIFICATION': 'Exact Data Match Classification',
    
    # Defender / Security
    'WINDEFATP': 'Microsoft Defender for Endpoint',
    'ATP_ENTERPRISE': 'Microsoft Defender for Office 365 (Plan 1)',
    'THREAT_INTELLIGENCE': 'Microsoft Defender for Office 365 (Plan 2)',
    'MTP': 'Microsoft Defender XDR',
    'SAFEDOCS': 'Safe Documents',
    'ATA': 'Microsoft Defender for Identity',
    'ADALLOM_S_O365': 'Microsoft Defender for Cloud Apps for Office 365',
    'ADALLOM_S_STANDALONE': 'Microsoft Defender for Cloud Apps',
    'Defender_for_Iot_Enterprise': 'Microsoft Defender for IoT',
    'RMS_S_ENTERPRISE': 'Azure Rights Management',
    'RMS_S_PREMIUM': 'Azure Information Protection Premium P1',
    'RMS_S_PREMIUM2': 'Azure Information Protection Premium P2',
    
    # Power Platform
    'POWERAPPS_O365_P1': 'Power Apps for Office 365 (Plan 1)',
    'POWERAPPS_O365_P2': 'Power Apps for Office 365 (Plan 2)',
    'POWERAPPS_O365_P3': 'Power Apps for Office 365 (Plan 3)',
    'FLOW_O365_P1': 'Power Automate for Office 365 (Plan 1)',
    'FLOW_O365_P2': 'Power Automate for Office 365 (Plan 2)',
    'FLOW_O365_P3': 'Power Automate for Office 365 (Plan 3)',
    'FLOW_P2_VIRAL': 'Power Automate (Free)',
    'FLOW_VIRTUAL_AGENT_USL': 'Power Automate for Power Virtual Agents',
    'FLOW_VIRTUAL_AGENT_BASE_MESSAGES': 'Power Automate for Power Virtual Agents (Base)',
    'FLOW_CCI_BOTS': 'Power Automate for Copilot Studio',
    'DYN365_CDS_O365_P1': 'Common Data Service for Office 365 (Plan 1) - Dynamics',
    'DYN365_CDS_O365_P2': 'Common Data Service for Office 365 (Plan 2) - Dynamics',
    'DYN365_CDS_O365_P3': 'Common Data Service for Office 365 (Plan 3) - Dynamics',
    'CDS_O365_P1': 'Common Data Service for Office 365 (Plan 1)',
    'CDS_O365_P2': 'Common Data Service for Office 365 (Plan 2)',
    'CDS_O365_P3': 'Common Data Service for Office 365 (Plan 3)',
    'DYN365_CDS_VIRAL': 'Common Data Service (Viral)',
    'CDS_VIRTUAL_AGENT_USL': 'Common Data Service for Power Virtual Agents',
    'CDS_VIRTUAL_AGENT_BASE_MESSAGES': 'Common Data Service for Power Virtual Agents (Base)',
    'DYN365_CDS_CCI_BOTS': 'Common Data Service for Copilot Studio',
    'BI_AZURE_P2': 'Power BI Pro',
    
    # Copilot / Virtual Agents
    'POWER_VIRTUAL_AGENTS_O365_P3': 'Power Virtual Agents for Office 365',
    'VIRTUAL_AGENT_USL': 'Power Virtual Agents',
    'VIRTUAL_AGENT_BASE_MESSAGES': 'Power Virtual Agents (Base)',
    'CCIBOTS_PRIVPREV_VIRAL': 'Copilot Studio (Viral)',
    'COPILOT_STUDIO_IN_COPILOT_FOR_M365': 'Copilot Studio in Microsoft 365 Copilot',
    'M365_COPILOT_INTELLIGENT_SEARCH': 'Microsoft 365 Copilot - Intelligent Search',
    'M365_COPILOT_BUSINESS_CHAT': 'Microsoft 365 Copilot - Business Chat',
    'M365_COPILOT_TEAMS': 'Microsoft 365 Copilot in Teams',
    'M365_COPILOT_APPS': 'Microsoft 365 Copilot in Apps',
    'M365_COPILOT_CONNECTORS': 'Microsoft 365 Copilot Connectors',
    'M365_COPILOT_SHAREPOINT': 'Microsoft 365 Copilot in SharePoint',
    'GRAPH_CONNECTORS_COPILOT': 'Graph Connectors for Copilot',
    'GRAPH_CONNECTORS_SEARCH_INDEX': 'Graph Connectors Search Index',
    
    # Office Apps
    'MCOEV_VIRTUALUSER': 'Audio Conferencing',
    'MESH_IMMERSIVE_FOR_TEAMS': 'Mesh Immersive Spaces for Teams',
    'STREAM_O365_E5': 'Microsoft Stream (Plan 2)',
    'VIVA_INSIGHTS_MYANALYTICS_FULL': 'Viva Insights - MyAnalytics (Full)',
    'WINDOWSUPDATEFORBUSINESS_DEPLOYMENTSERVICE': 'Windows Update for Business',
    'OFFICESUBSCRIPTION': 'Microsoft 365 Apps for Enterprise',
    'OFFICE_FORMS_PLAN_2': 'Microsoft Forms (Plan 2)',
    'OFFICE_FORMS_PLAN_3': 'Microsoft Forms (Plan 3)',
    'FORMS_PLAN_E1': 'Microsoft Forms (Plan E1)',
    'FORMS_PLAN_E5': 'Microsoft Forms (Plan E5)',
    'PROJECTWORKMANAGEMENT': 'Microsoft Planner',
    'PROJECTWORKMANAGEMENT_PLANNER': 'Microsoft Planner and Project',
    'PROJECT_O365_P1': 'Project for Office 365 (Plan 1)',
    'PROJECT_O365_P2': 'Project for Office 365 (Plan 2)',
    'PROJECT_O365_P3': 'Project for Office 365 (Plan 3)',
    'SWAY': 'Sway',
    'BPOS_S_TODO_1': 'Microsoft To Do (Plan 1)',
    'BPOS_S_TODO_2': 'Microsoft To Do (Plan 2)',
    'BPOS_S_TODO_3': 'Microsoft To Do (Plan 3)',
    'WHITEBOARD_PLAN1': 'Whiteboard (Plan 1)',
    'WHITEBOARD_PLAN2': 'Whiteboard (Plan 2)',
    'WHITEBOARD_PLAN3': 'Whiteboard (Plan 3)',
    'CLIPCHAMP': 'Clipchamp',
    'EXCEL_PREMIUM': 'Excel Advanced Analytics',
    'MICROSOFT_LOOP': 'Microsoft Loop',
    
    # SharePoint / OneDrive
    'SHAREPOINTENTERPRISE': 'SharePoint (Plan 2)',
    'SHAREPOINTSTANDARD': 'SharePoint (Plan 1)',
    'SHAREPOINTWAC': 'Office for the Web (SharePoint)',
    'OFFICEMOBILE_SUBSCRIPTION': 'Office for the Web (Mobile)',
    'ONEDRIVE_BASIC': 'OneDrive for Business (Basic)',
    'ONEDRIVE_BASIC_P2': 'OneDrive for Business (Plan 2)',
    
    # Exchange
    'EXCHANGE_S_ENTERPRISE': 'Exchange Online (Plan 2)',
    'EXCHANGE_S_STANDARD': 'Exchange Online (Plan 1)',
    'EXCHANGE_S_DESKLESS': 'Exchange Online Kiosk',
    'EXCHANGEDESKLESS': 'Exchange Online Kiosk (Deskless)',
    'EXCHANGEDESKLESS_GOV': 'Exchange Online Kiosk (Government)',
    'EXCHANGE_S_ARCHIVE_ADDON': 'Exchange Online Archiving',
    'EXCHANGE_S_FOUNDATION': 'Exchange Foundation',
    'EXCHANGE_ANALYTICS': 'Exchange Analytics',
    'MCOEV': 'Microsoft 365 Phone System',
    'MCOMEETADV': 'Microsoft 365 Audio Conferencing',
    
    # Teams
    'TEAMS1': 'Microsoft Teams',
    'MCOSTANDARD': 'Skype for Business Online (Plan 2)',
    'MCOSTANDARD_GOV': 'Skype for Business Online (Plan 2) - Government',
    'MCOIMP': 'Skype for Business Online (Plan 1)',
    'MCO_VIRTUAL_APPT': 'Virtual Appointments',
    'MCO_VIRTUAL_APPT_PREMIUM': 'Virtual Appointments Premium',
    'TEAMSPRO_MGMT': 'Teams Premium - Management',
    'TEAMSPRO_WEBINAR': 'Teams Premium - Webinars',
    'TEAMSPRO_PROTECTION': 'Teams Premium - Protection',
    'TEAMSPRO_CUST': 'Teams Premium - Customer',
    'TEAMS_PREMIUM_CUSTOMER': 'Teams Premium - Customer Experience',
    'TEAMSPRO_VIRTUALAPPT': 'Teams Premium - Virtual Appointments',
    'TEAMWORK_ANALYTICS': 'Microsoft Teams Teamwork Analytics',
    'MICROSOFT_ECDN': 'Microsoft eCDN',
    'MESH': 'Mesh',
    'MESH_IMMERSIVE': 'Mesh Immersive Spaces (Standalone)',
    'MESH_IMMERSIVE_FOR_TEAMS': 'Mesh Immersive Spaces for Teams',
    'MESH_AVATARS_FOR_TEAMS': 'Mesh Avatars for Teams',
    'MESH_AVATARS_ADDITIONAL_FOR_TEAMS': 'Mesh Avatars for Teams (Additional)',
    'PLACES_CORE': 'Microsoft Places (Core)',
    'PLACES_ENHANCED': 'Microsoft Places (Enhanced)',
    'MICROSOFT_PLACES': 'Microsoft Places',
    'QUEUES_APP': 'Queues App',
    
    # Viva
    'VIVA_LEARNING_SEEDED': 'Viva Learning (Seeded)',
    'VIVAENGAGE_CORE': 'Viva Engage Core',
    'VIVA_GOALS': 'Viva Goals',
    'WORKPLACE_ANALYTICS_INSIGHTS_USER': 'Viva Insights',
    'WORKPLACE_ANALYTICS_INSIGHTS_BACKEND': 'Viva Insights (Backend)',
    'VIVA_INSIGHTS_BACKEND': 'Viva Insights Backend',
    'MYANALYTICS_P1': 'MyAnalytics (Plan 1)',
    'MYANALYTICS_P2': 'Insights by MyAnalytics',
    'MYANALYTICS_P3': 'MyAnalytics (Plan 3)',
    'MICROSOFT_MYANALYTICS_FULL': 'MyAnalytics (Full)',
    'INSIGHTS_BY_MYANALYTICS': 'Insights by MyAnalytics',
    'PEOPLE_SKILLS_FOUNDATION': 'People Skills Foundation',
    
    # Yammer
    'YAMMER_ENTERPRISE': 'Yammer Enterprise',
    
    # Other M365 Services
    'DESKLESS': 'Microsoft StaffHub',
    'NUCLEUS': 'Nucleus',
    'WINDOWS_AUTOPATCH': 'Windows Autopatch',
    
    # Windows
    'WIN10_PRO_ENT_SUB': 'Windows 10/11 Enterprise',
    'WIN10_ENT': 'Windows 10/11 Enterprise (E3)',
    'WIN10_VDA_E3': 'Windows 10/11 Enterprise VDA',
    'WINDOWSUPDATEFORBUSINESS_DEPLOYMENTSERVICE': 'Windows Update for Business',
    'UNIVERSAL_PRINT_01': 'Universal Print',
    
    # Other
    'KAIZALA_STANDALONE': 'Microsoft Kaizala',
    'MICROSOFT_SEARCH': 'Microsoft Search (Service)',
    'MICROSOFTBOOKINGS': 'Microsoft Bookings (Service)',
    'STREAM_O365_E1': 'Microsoft Stream for Office 365 (E1)',
    'STREAM_O365_E3': 'Microsoft Stream for Office 365 (E3)',
    'STREAM_O365_E5': 'Microsoft Stream (Plan 2)',
    'PAM_ENTERPRISE': 'Privileged Access Management',
    'M365_LIGHTHOUSE_CUSTOMER_PLAN1': 'Microsoft 365 Lighthouse',
    'Bing_Chat_Enterprise': 'Bing Chat Enterprise',
}


def get_friendly_sku_name(technical_sku_name: str) -> str:
    """
    Convert a technical SKU name to a friendly display name.
    
    Args:
        technical_sku_name: Technical SKU name like 'Microsoft_365_Copilot'
        
    Returns:
        Friendly name like 'Microsoft 365 Copilot', or the original name if no mapping exists
    """
    # Try exact match first
    if technical_sku_name in SKU_FRIENDLY_NAMES:
        return SKU_FRIENDLY_NAMES[technical_sku_name]
    
    # Try basic transformation: replace underscores with spaces
    friendly = technical_sku_name.replace('_', ' ')
    
    # Fix common patterns
    friendly = friendly.replace('  ', ' ')  # Remove double spaces
    friendly = friendly.replace('( ', '(')  # Fix parentheses spacing
    friendly = friendly.replace(' )', ')')
    
    return friendly


def get_friendly_plan_name(service_plan_name: str) -> str:
    """
    Get the friendly name for a service plan.
    
    Args:
        service_plan_name: Technical service plan name
        
    Returns:
        Friendly display name or original name if not found
    """
    return SERVICE_PLAN_FRIENDLY_NAMES.get(service_plan_name, service_plan_name)
