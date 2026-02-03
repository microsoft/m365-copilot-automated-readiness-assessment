"""Service validation logic for orchestrator."""

from .spinner import get_timestamp


def validate_and_prepare_services(services):
    """Validate service selection and prepare service flags.
    
    Args:
        services: List of services to analyze. Empty list or None = all services.
        
    Returns:
        Dict containing run_* flags and metadata about selected services.
        Returns None if validation fails.
    """
    # Normalize services parameter
    if services is None:
        services = []
    
    # Validate services
    valid_services = {"M365", "Entra", "Defender", "Purview", "Power Platform", "Copilot Studio"}
    invalid_services = [s for s in services if s not in valid_services]
    if invalid_services:
        print(f"[{get_timestamp()}] ⚠️  Invalid services specified: {', '.join(invalid_services)}")
        print(f"[{get_timestamp()}] ℹ️  Valid services are: {', '.join(sorted(valid_services))}")
        return None
    
    # Determine which services to run (empty = all)
    run_all = len(services) == 0
    run_m365 = run_all or "M365" in services
    run_entra = run_all or "Entra" in services
    run_defender = run_all or "Defender" in services
    run_purview = run_all or "Purview" in services
    run_power_platform = run_all or "Power Platform" in services
    run_copilot_studio = run_all or "Copilot Studio" in services
    
    # Count services that will be loaded
    services_to_load = sum([run_m365, run_entra, run_defender, run_purview, run_power_platform, run_copilot_studio])
    
    return {
        'run_all': run_all,
        'run_m365': run_m365,
        'run_entra': run_entra,
        'run_defender': run_defender,
        'run_purview': run_purview,
        'run_power_platform': run_power_platform,
        'run_copilot_studio': run_copilot_studio,
        'services_to_load': services_to_load,
        'services': services
    }
