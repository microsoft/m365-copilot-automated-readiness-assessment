"""Service pipeline functions for orchestrator."""

import os
from spinner import get_timestamp, _stdout_lock
from orchestrator_powershell import collect_purview_data_via_powershell


def create_pipelines(client, services_and_licenses, tenant_id, service_config):
    """Create all service pipeline functions with shared context.
    
    Args:
        client: Microsoft Graph client
        services_and_licenses: ServicesAndLicenses container
        tenant_id: Azure tenant ID
        service_config: Dict with run_* flags from validate_and_prepare_services()
        
    Returns:
        Dict of pipeline functions keyed by service name
    """
    # Extract flags for easier access
    run_m365 = service_config['run_m365']
    run_entra = service_config['run_entra']
    run_defender = service_config['run_defender']
    run_purview = service_config['run_purview']
    run_power_platform = service_config['run_power_platform']
    run_copilot_studio = service_config['run_copilot_studio']
    
    # Define pipeline functions as closures over shared context
    async def m365_pipeline():
        """M365: Gather client data, then process"""
        if not run_m365:
            return ([], [])
        
        try:
            # Gathering phase (has its own progress bar inside get_m365_client)
            from get_m365_client import get_m365_client
            m365_client = await get_m365_client(client)
            
            # Processing phase with progress bar
            import sys
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   M365 Data Processing    [░░░░░░░░░░░░░░░░░░░░]   0%')
                sys.stdout.flush()
            
            from get_m365_info import get_m365_info
            result = await get_m365_info(client, services_and_licenses, m365_client)
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ M365 Data Processing    [████████████████████] 100%\n')
                sys.stdout.flush()
            
            return result
        except Exception as e:
            import traceback
            print(f"\n[ERROR] M365 pipeline failed: {e}")
            traceback.print_exc()
            return ([], [])
    
    async def entra_pipeline():
        """Entra: Gather client data, then process"""
        if not run_entra:
            return {'available': False, 'recommendations': []}
        
        try:
            # Gathering phase (has its own progress bar inside get_entra_client)
            from get_entra_client import get_entra_client
            entra_client = await get_entra_client(client, tenant_id)
            
            # Processing phase with progress bar
            import sys
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   Entra Data Processing   [░░░░░░░░░░░░░░░░░░░░]   0%')
                sys.stdout.flush()
            
            from get_entra_info import get_entra_info
            result = await get_entra_info(client, services_and_licenses, entra_client)
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Entra Data Processing   [████████████████████] 100%\n')
                sys.stdout.flush()
            
            return result
        except Exception as e:
            return {'available': False, 'recommendations': []}
    
    async def purview_pipeline():
        """Purview: Gather client data, then process"""
        if not run_purview:
            return {'available': False, 'recommendations': []}
        
        try:
            # Check if Purview data is available from stdin
            purview_data_source = os.environ.get('PURVIEW_DATA_SOURCE')
            
            # If data not available via stdin, invoke PowerShell to collect it
            if purview_data_source != 'stdin':
                # Gathering phase - invoke PowerShell
                collection_success = await collect_purview_data_via_powershell()
                if not collection_success:
                    return {'available': False, 'recommendations': []}
            else:
                # Data available via stdin - normal path
                with _stdout_lock:
                    import sys
                    sys.stdout.write(f'\r[{get_timestamp()}]   Purview Data Gathering  [░░░░░░░░░░░░░░░░░░░░]   0%')
                    sys.stdout.flush()
            
            from get_purview_client import get_purview_client
            purview_client = await get_purview_client(client)
            
            if purview_data_source == 'stdin':
                with _stdout_lock:
                    import sys
                    sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Purview Data Gathering  [████████████████████] 100%\n')
                    sys.stdout.flush()
            
            if purview_client is None:
                return {'available': False, 'recommendations': []}
            
            # Processing phase
            with _stdout_lock:
                import sys
                sys.stdout.write(f'\r[{get_timestamp()}]   Purview Data Processing [░░░░░░░░░░░░░░░░░░░░]   0%')
                sys.stdout.flush()
            
            from get_purview_info import get_purview_info
            result = await get_purview_info(client, services_and_licenses, purview_client)
            
            with _stdout_lock:
                import sys
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Purview Data Processing [████████████████████] 100%\n')
                sys.stdout.flush()
            
            return result
        except Exception as e:
            return {'available': False, 'recommendations': []}
    
    async def defender_pipeline():
        """Defender: Gather client data, then process"""
        if not run_defender:
            return {'available': False, 'recommendations': []}
        
        try:
            # Gathering phase
            import sys
            
            from get_defender_client import get_defender_client
            defender_client = await get_defender_client(tenant_id, client)
            
            if defender_client is None:
                return {'available': False, 'recommendations': []}
            
            # Processing phase
            with _stdout_lock:
                sys.stdout.write(f'[{get_timestamp()}]   Defender Data Processing[░░░░░░░░░░░░░░░░░░░░]   0%')
                sys.stdout.flush()
            
            from get_defender_info import get_defender_info
            purview_client_for_defender = None
            result = await get_defender_info(client, defender_client, services_and_licenses, purview_client_for_defender)
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Defender Data Processing[████████████████████] 100%\n')
                sys.stdout.flush()
            
            return result
        except Exception as e:
            with _stdout_lock:
                print(f"[{get_timestamp()}] ERROR in defender_pipeline: {str(e)}")
                import traceback
                traceback.print_exc()
            return {'available': False, 'recommendations': []}
    
    async def power_platform_pipeline():
        """Power Platform: Gather client data, then process"""
        if not run_power_platform:
            return {'available': False, 'recommendations': []}
        
        try:
            # Data already collected in pre-flight (or not available)
            # Just gather and process
            import sys
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   Power Platform Gathering[░░░░░░░░░░░░░░░░░░░░]   0%')
                sys.stdout.flush()
            
            from get_power_platform_client import get_power_platform_client
            pp_client = await get_power_platform_client(tenant_id)
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Power Platform Gathering[████████████████████] 100%\n')
                sys.stdout.flush()
            
            if pp_client is None:
                with _stdout_lock:
                    sys.stdout.write(f'[{get_timestamp()}]   ⚠️  Power Platform client returned None - check permissions or authentication\n')
                    sys.stdout.flush()
                return {'available': False, 'recommendations': []}
            
            # Processing phase
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   Power Platform Processing[░░░░░░░░░░░░░░░░░░░░]   0%')
                sys.stdout.flush()
            
            from get_power_platform_info import get_power_platform_info
            result = await get_power_platform_info(client, services_and_licenses, pp_client)
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Power Platform Processing[████████████████████] 100%\n')
                sys.stdout.flush()
            
            return result
        except Exception as e:
            with _stdout_lock:
                sys.stdout.write(f'[{get_timestamp()}]   ✗ Power Platform pipeline error: {type(e).__name__}: {e}\n')
                sys.stdout.flush()
            import traceback
            traceback.print_exc()
            return {'available': False, 'recommendations': []}
    
    async def copilot_studio_pipeline():
        """Copilot Studio: Gather client data (reuses PP client), then process"""
        if not run_copilot_studio:
            return {'available': False, 'recommendations': []}
        
        try:
            # Gathering phase (uses same data as Power Platform from pre-flight)
            import sys
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   Copilot Studio Gathering[░░░░░░░░░░░░░░░░░░░░]   0%')
                sys.stdout.flush()
            
            from get_power_platform_client import get_power_platform_client
            pp_client = await get_power_platform_client(tenant_id)
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Copilot Studio Gathering[████████████████████] 100%\n')
                sys.stdout.flush()
            
            # pp_client can be None (no enrichment data) - that's OK!
            # get_copilot_studio_info will generate basic recommendations from Graph API
            
            # Processing phase
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   Copilot Studio Processing[░░░░░░░░░░░░░░░░░░░░]   0%')
                sys.stdout.flush()
            
            from get_copilot_studio_info import get_copilot_studio_info
            result = await get_copilot_studio_info(client, services_and_licenses, pp_client)
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Copilot Studio Processing[████████████████████] 100%\n')
                sys.stdout.flush()
            
            return result
        except Exception as e:
            with _stdout_lock:
                sys.stdout.write(f'[{get_timestamp()}]   ✗ Copilot Studio pipeline error: {type(e).__name__}: {e}\n')
                sys.stdout.flush()
            import traceback
            traceback.print_exc()
            return {'available': False, 'recommendations': []}
    
    # Return dict of pipelines
    return {
        'm365': m365_pipeline,
        'entra': entra_pipeline,
        'purview': purview_pipeline,
        'defender': defender_pipeline,
        'power_platform': power_platform_pipeline,
        'copilot_studio': copilot_studio_pipeline
    }
