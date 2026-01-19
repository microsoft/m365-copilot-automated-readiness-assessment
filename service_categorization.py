"""
Service categorization and reference data for Microsoft 365 service plans.
Provides categorization logic and baseline reference data for service plans by SKU.
"""

# Service plan to service category mapping
# All keys are uppercase for case-insensitive matching
SERVICE_PLAN_MAPPING = {
    # ENTRA
    'AAD_GOVERNANCE': 'entra', 'AAD_PREMIUM': 'entra', 'AAD_PREMIUM_CONDITIONAL_ACCESS': 'entra',
    'AAD_PREMIUM_IDENTITY_PROTECTION': 'entra', 'AAD_PREMIUM_P1': 'entra', 'AAD_PREMIUM_P2': 'entra',
    'ENTRA_INSIGHTS': 'entra', 'ENTRA_INTERNET_ACCESS': 'entra', 'ENTRA_INTERNET_ACCESS_FRONTLINE': 'entra',
    'ENTRA_PRIVATE_ACCESS': 'entra', 'ENTRA_PRIVATE_ACCESS_CA': 'entra', 'INTUNE_A': 'entra', 'MFA_PREMIUM': 'entra',
    
    # PURVIEW
    'AIP_P1': 'purview', 'AIP_P2': 'purview', 'COMMUNICATIONS_COMPLIANCE': 'purview', 'COMMUNICATIONS_DLP': 'purview',
    'CONTENTEXPLORER_STANDARD': 'purview', 'CONTENTEXPLORER_STANDARD_ACTIVITY': 'purview', 'CONTENT_EXPLORER': 'purview',
    'CUSTOMERLOCKBOXA_ENTERPRISE': 'purview', 'CUSTOMER_KEY': 'purview', 'DATAINVESTIGATION': 'purview',
    'DATA_INVESTIGATIONS': 'purview', 'EDISCOVERY': 'purview', 'EQUIVIO_ANALYTICS': 'purview',
    'EQUIVIO_ANALYTICS_EDM': 'purview', 'INFORMATION_BARRIERS': 'purview', 'INFORMATION_PROTECTION_ANALYTICS': 'purview',
    'INFORMATION_PROTECTION_COMPLIANCE_PREMIUM': 'purview', 'INFO_GOVERNANCE': 'purview', 'INSIDER_RISK': 'purview',
    'INSIDER_RISK_MANAGEMENT': 'purview', 'LOCKBOX_ENTERPRISE': 'purview', 'M365_ADVANCED_AUDITING': 'purview',
    'M365_AUDIT_PLATFORM': 'purview', 'MICROSOFTENDPOINTDLP': 'purview', 'MICROSOFT_COMMUNICATION_COMPLIANCE': 'purview',
    'MIP_S_CLP1': 'purview', 'MIP_S_CLP2': 'purview', 'MIP_S_EXCHANGE': 'purview', 'ML_CLASSIFICATION': 'purview',
    'PAM_ENTERPRISE': 'purview', 'PREMIUM_ENCRYPTION': 'purview', 'PURVIEW_DISCOVERY': 'purview',
    'RECORDS_MANAGEMENT': 'purview', 'RMS_S_ENTERPRISE': 'purview', 'RMS_S_PREMIUM': 'purview', 'RMS_S_PREMIUM2': 'purview',
    
    # DEFENDER
    'ADALLOM_S_DISCOVERY': 'defender', 'ADALLOM_S_O365': 'defender', 'ADALLOM_S_STANDALONE': 'defender',
    'ATA': 'defender', 'ATP_ENTERPRISE': 'defender', 'COPILOT_DATA_GOVERNANCE': 'defender',
    'COPILOT_SECURITY_POSTURE': 'defender', 'COPILOT_THREAT_INTELLIGENCE': 'defender', 'DEFENDER_ENDPOINT_ONBOARDING': 'defender',
    'DEFENDER_FOR_IOT': 'defender', 'DEFENDER_FOR_IOT_ENTERPRISE': 'defender', 'DEFENDER_INSIGHTS': 'defender',
    'DEFENDER_XDR_ACTIVATION': 'defender', 'EOP_ENTERPRISE_PREMIUM': 'defender', 'MTP': 'defender',
    'SAFEDOCS': 'defender', 'THREAT_INTELLIGENCE': 'defender', 'WINDEFATP': 'defender',
    
    # COPILOT_STUDIO
    'CCIBOTS_PRIVPREV_VIRAL': 'copilot_studio', 'CDS_VIRTUAL_AGENT_BASE_MESSAGES': 'copilot_studio',
    'CDS_VIRTUAL_AGENT_USL': 'copilot_studio', 'COPILOT_STUDIO_IN_COPILOT_FOR_M365': 'copilot_studio',
    'FLOW_VIRTUAL_AGENT_BASE_MESSAGES': 'copilot_studio', 'FLOW_VIRTUAL_AGENT_USL': 'copilot_studio',
    'POWER_VIRTUAL_AGENTS': 'copilot_studio', 'POWER_VIRTUAL_AGENTS_BASE': 'copilot_studio',
    'POWER_VIRTUAL_AGENTS_O365_P3': 'copilot_studio', 'VIRTUAL_AGENT_BASE_MESSAGES': 'copilot_studio',
    'VIRTUAL_AGENT_USL': 'copilot_studio',
    
    # POWER_PLATFORM
    'AI_BUILDER_MODELS': 'power_platform', 'BI_AZURE_P2': 'power_platform', 'CDS_O365_P1': 'power_platform',
    'CDS_O365_P2': 'power_platform', 'CDS_O365_P3': 'power_platform', 'CDS_VIRAL': 'power_platform',
    'DLP_GOVERNANCE': 'power_platform', 'DYN365_CDS_CCI_BOTS': 'power_platform', 'DYN365_CDS_O365_P1': 'power_platform',
    'DYN365_CDS_O365_P2': 'power_platform', 'DYN365_CDS_O365_P3': 'power_platform', 'DYN365_CDS_VIRAL': 'power_platform',
    'FLOW_CCI_BOTS': 'power_platform', 'FLOW_FREE': 'power_platform', 'FLOW_O365_P3': 'power_platform',
    'FLOW_P2_VIRAL': 'power_platform', 'POWERAPPS_O365_P3': 'power_platform',
    
    # M365
    'BING_CHAT_ENTERPRISE': 'm365', 'BPOS_S_TODO_3': 'm365', 'CLIPCHAMP': 'm365', 'DESKLESS': 'm365',
    'EXCEL_PREMIUM': 'm365', 'EXCHANGEDESKLESS': 'm365', 'EXCHANGEDESKLESS_GOV': 'm365', 'EXCHANGE_ANALYTICS': 'm365',
    'EXCHANGE_S_ARCHIVE_ADDON': 'm365', 'EXCHANGE_S_DESKLESS': 'm365', 'EXCHANGE_S_ENTERPRISE': 'm365',
    'EXCHANGE_S_FOUNDATION': 'm365', 'EXCHANGE_S_STANDARD': 'm365', 'FORMS_PLAN_E1': 'm365', 'FORMS_PLAN_E5': 'm365',
    'GRAPH_CONNECTORS_COPILOT': 'm365', 'GRAPH_CONNECTORS_SEARCH_INDEX': 'm365', 'INSIGHTS_BY_MYANALYTICS': 'm365',
    'INTUNE_O365': 'm365', 'INTUNE_SUITE': 'm365', 'KAIZALA_STANDALONE': 'm365', 'M365_COPILOT_APPS': 'm365',
    'M365_COPILOT_BUSINESS_CHAT': 'm365', 'M365_COPILOT_CONNECTORS': 'm365', 'M365_COPILOT_INTELLIGENT_SEARCH': 'm365',
    'M365_COPILOT_SHAREPOINT': 'm365', 'M365_COPILOT_TEAMS': 'm365', 'M365_LIGHTHOUSE_CUSTOMER_PLAN1': 'm365',
    'MCOEV': 'm365', 'MCOEV_VIRTUALUSER': 'm365', 'MCOIMP': 'm365', 'MCOMEETADV': 'm365', 'MCOSTANDARD': 'm365',
    'MCOSTANDARD_GOV': 'm365', 'MCO_VIRTUAL_APPT': 'm365', 'MCO_VIRTUAL_APPT_PREMIUM': 'm365', 'MESH': 'm365',
    'MESH_AVATARS_ADDITIONAL_FOR_TEAMS': 'm365', 'MESH_AVATARS_FOR_TEAMS': 'm365', 'MESH_IMMERSIVE': 'm365',
    'MESH_IMMERSIVE_FOR_TEAMS': 'm365', 'MICROSOFTBOOKINGS': 'm365', 'MICROSOFT_ECDN': 'm365', 'MICROSOFT_LOOP': 'm365',
    'MICROSOFT_MYANALYTICS_FULL': 'm365', 'MICROSOFT_PLACES': 'm365', 'MICROSOFT_SEARCH': 'm365', 'MYANALYTICS_P1': 'm365',
    'MYANALYTICS_P2': 'm365', 'MYANALYTICS_P3': 'm365', 'NUCLEUS': 'm365', 'OFFICEMOBILE_SUBSCRIPTION': 'm365',
    'OFFICESUBSCRIPTION': 'm365', 'ONEDRIVE_BASIC_P2': 'm365', 'PEOPLE_SKILLS_FOUNDATION': 'm365', 'PLACES_CORE': 'm365',
    'PLACES_ENHANCED': 'm365', 'PROJECTWORKMANAGEMENT': 'm365', 'PROJECTWORKMANAGEMENT_PLANNER': 'm365',
    'PROJECT_O365_P1': 'm365', 'PROJECT_O365_P3': 'm365', 'QUEUES_APP': 'm365', 'SHAREPOINTENTERPRISE': 'm365', 'SHAREPOINTSTANDARD': 'm365',
    'SHAREPOINTWAC': 'm365', 'STREAM_O365_E5': 'm365', 'SWAY': 'm365', 'TEAMS1': 'm365', 'TEAMSPRO_CUST': 'm365',
    'TEAMSPRO_MGMT': 'm365', 'TEAMSPRO_PROTECTION': 'm365', 'TEAMSPRO_VIRTUALAPPT': 'm365', 'TEAMSPRO_WEBINAR': 'm365',
    'TEAMS_PREMIUM_CUSTOMER': 'm365', 'TEAMWORK_ANALYTICS': 'm365', 'UNIVERSAL_PRINT_01': 'm365', 'VIVAENGAGE_CORE': 'm365',
    'VIVA_GOALS': 'm365', 'VIVA_INSIGHTS_BACKEND': 'm365', 'VIVA_INSIGHTS_MYANALYTICS_FULL': 'm365',
    'VIVA_LEARNING_SEEDED': 'm365', 'WHITEBOARD_PLAN3': 'm365', 'WIN10_ENT': 'm365', 'WIN10_PRO_ENT_SUB': 'm365',
    'WIN10_VDA_E3': 'm365', 'WINDOWSUPDATEFORBUSINESS_DEPLOYMENTSERVICE': 'm365', 'WINDOWS_AUTOPATCH': 'm365',
    'WORKPLACE_ANALYTICS_INSIGHTS_BACKEND': 'm365', 'WORKPLACE_ANALYTICS_INSIGHTS_USER': 'm365', 'YAMMER_ENTERPRISE': 'm365',
}

# Reference data for known SKUs
# This is a partial list - expand as needed
SKU_REFERENCE = {
    '18a4bd3f-0b5b-4887-b04f-61dd0ee15f5e': {  # Microsoft_365_E5_(no_Teams)
        'sku_part_number': 'Microsoft_365_E5_(no_Teams)',
        'expected_plans': {
            'entra': [
                'AAD_PREMIUM', 'AAD_PREMIUM_P2', 'MFA_PREMIUM', 'INTUNE_A', 'INTUNE_O365'
            ],
            'purview': [
                'INSIDER_RISK_MANAGEMENT', 'COMMUNICATIONS_COMPLIANCE', 'PURVIEW_DISCOVERY',
                'PREMIUM_ENCRYPTION', 'RECORDS_MANAGEMENT', 'INSIDER_RISK', 'INFO_GOVERNANCE',
                'MICROSOFTENDPOINTDLP', 'DATA_INVESTIGATIONS', 'COMMUNICATIONS_DLP',
                'MICROSOFT_COMMUNICATION_COMPLIANCE'
            ],
            'defender': [
                'THREAT_INTELLIGENCE', 'ATP_ENTERPRISE', 'ATA', 'WINDEFATP', 'SAFEDOCS',
                'MTP', 'DATA_INVESTIGATIONS', 'Defender_for_Iot_Enterprise'
            ],
            'power_platform': [
                'POWER_VIRTUAL_AGENTS_O365_P3', 'FLOW_O365_P3', 'POWERAPPS_O365_P3',
                'CDS_O365_P3', 'DYN365_CDS_O365_P3'
            ],
            'copilot_studio': [
                'POWER_VIRTUAL_AGENTS_O365_P3'
            ]
        }
    },
    'cbdc14ab-d96c-4c30-b9f4-6ada7cdc1d46': {  # Microsoft_365_Business_Premium
        'sku_part_number': 'Microsoft_365_Business_Premium',
        'expected_plans': {
            'entra': [
                'AAD_PREMIUM', 'MFA_PREMIUM', 'INTUNE_O365'
            ],
            'purview': [
                'INFORMATION_PROTECTION', 'DLP', 'INFO_GOVERNANCE'
            ],
            'defender': [
                'ATP_ENTERPRISE', 'WINDEFATP'
            ],
            'power_platform': [
                'POWER_VIRTUAL_AGENTS_O365_P1', 'FLOW_O365_P1', 'POWERAPPS_O365_P1',
                'CDS_O365_P1'
            ]
        }
    },
    # Add more SKU references as needed
}


def get_sku_reference(sku_id: str):
    """
    Get reference data for a specific SKU.
    
    Args:
        sku_id: The SKU ID to look up
        
    Returns:
        Reference data dict or None if SKU not in reference
    """
    return SKU_REFERENCE.get(sku_id)


def get_expected_plans_for_service(sku_id: str, service_name: str):
    """
    Get expected service plans for a specific service category.
    
    Args:
        sku_id: The SKU ID
        service_name: Service category name (e.g., 'entra', 'purview')
        
    Returns:
        List of expected plan names or None
    """
    sku_ref = SKU_REFERENCE.get(sku_id)
    if not sku_ref:
        return None
    return sku_ref.get('expected_plans', {}).get(service_name, [])


def determine_service_type(plan_name):
    """
    Determine which service category a feature belongs to based on its name.
    Returns a single primary service category.
    
    Args:
        plan_name: The service plan name
        
    Returns:
        String indicating service category: 'entra', 'defender', 'purview', 
        'power_platform', 'copilot_studio', or 'm365' (default)
    """
    # Use exact plan name lookup from SERVICE_PLAN_MAPPING
    # Uppercase for case-insensitive matching
    return SERVICE_PLAN_MAPPING.get(plan_name.upper(), 'm365')
