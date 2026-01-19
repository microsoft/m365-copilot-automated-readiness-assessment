"""
Module for retrieving feature-specific recommendations
Uses modular recommendation files organized by service
"""

def get_recommendation(recommendation_type, feature_name, sku_name, status="Success", client=None, pp_client=None, pp_insights=None, purview_client=None, defender_client=None, defender_insights=None, entra_insights=None, m365_insights=None):
    """
    Get a feature-specific recommendation based on type
    
    Each service category (entra, defender, purview, etc.) has a dedicated folder
    containing individual recommendation files for each feature. This enables
    precise, feature-specific observations and recommendations focused on
    M365 Copilot and agent adoption.
    
    Args:
        recommendation_type: Type of recommendation to create (entra, defender, purview, etc.)
        feature_name: Technical service plan name (e.g., 'AAD_PREMIUM', 'MTP')
        sku_name: Name of the SKU containing the feature
        status: Provisioning status of the feature
        client: Optional Graph client for deployment checks
        pp_client: Optional Power Platform client for deployment checks
        pp_insights: Pre-computed Power Platform insights (performance optimization)
        purview_client: Optional Purview client for deployment checks
        defender_client: Optional Defender API client for security metrics enrichment
        defender_insights: Pre-computed Defender insights (performance optimization)
        entra_insights: Pre-computed Entra insights (performance optimization)
        m365_insights: Pre-computed M365 usage insights (performance optimization)
    
    Returns:
        dict: Feature-specific recommendation object with:
            - Service: Service category
            - Feature: Friendly feature name
            - Status: Provisioning status
            - Priority: Priority level (empty for successful observations)
            - Observation: Specific observation about the feature
            - Recommendation: Specific recommendation for adoption
            - LinkText: Feature-specific link text
            - LinkUrl: Feature-specific documentation URL
    """
    # Lazy load recommendation modules based on type
    if recommendation_type.lower() == "entra":
        from Recommendations.entra import get_feature_recommendation as get_entra_recommendation
        recommendation_func = get_entra_recommendation
    elif recommendation_type.lower() == "defender":
        from Recommendations.defender import get_feature_recommendation as get_defender_recommendation
        recommendation_func = get_defender_recommendation
    elif recommendation_type.lower() == "purview":
        from Recommendations.purview import get_feature_recommendation as get_purview_recommendation
        recommendation_func = get_purview_recommendation
    elif recommendation_type.lower() == "power_platform":
        from Recommendations.power_platform import get_feature_recommendation as get_power_platform_recommendation
        recommendation_func = get_power_platform_recommendation
    elif recommendation_type.lower() == "copilot_studio":
        from Recommendations.copilot_studio import get_feature_recommendation as get_copilot_studio_recommendation
        recommendation_func = get_copilot_studio_recommendation
    elif recommendation_type.lower() == "m365":
        from Recommendations.m365 import get_feature_recommendation as get_m365_recommendation
        recommendation_func = get_m365_recommendation
    else:
        raise ValueError(f"Unknown recommendation type: {recommendation_type}")
    
    # Route to appropriate service-specific function with relevant clients
    if recommendation_type.lower() in ['power_platform', 'copilot_studio']:
        return recommendation_func(feature_name, sku_name, status, client=client, pp_client=pp_client, pp_insights=pp_insights)
    elif recommendation_type.lower() == 'purview':
        return recommendation_func(feature_name, sku_name, status, client=client, purview_client=purview_client)
    elif recommendation_type.lower() == 'defender':
        return recommendation_func(feature_name, sku_name, status, client=client, defender_client=defender_client, defender_insights=defender_insights)
    elif recommendation_type.lower() == 'entra':
        return recommendation_func(feature_name, sku_name, status, client=client, entra_insights=entra_insights)
    elif recommendation_type.lower() == 'm365':
        return recommendation_func(feature_name, sku_name, status, client=client, m365_insights=m365_insights)
    else:
        return recommendation_func(feature_name, sku_name, status, client=client)
