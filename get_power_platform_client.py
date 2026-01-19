"""
Power Platform Management API Client
Provides authenticated access to Power Platform APIs for deployment checks.
Fetches and caches: environments, flows, apps, connectors for Copilot adoption insights.
"""
import httpx
import asyncio
import json
import os
import sys
from azure.identity.aio import AzureCliCredential
from spinner import get_timestamp

# Power Platform Management API base URL
# Note: Power Platform has 4 separate API bases:
# - api.bap.microsoft.com: Business Application Platform (environments, DLP)
# - api.flow.microsoft.com: Power Automate flows (requires separate token!)
# - api.powerplatform.com: Canvas apps and governance (requires environment subdomain)
# - crm.dynamics.com: Dataverse (solution-aware resources)
POWER_PLATFORM_API_BASE = "https://api.bap.microsoft.com"
POWER_PLATFORM_SCOPE = "https://api.bap.microsoft.com/.default"
FLOW_API_BASE = "https://api.flow.microsoft.com"
FLOW_API_SCOPE = "https://service.flow.microsoft.com/.default"  # Different scope for Flow admin API

def load_power_platform_data_from_stdin():
    """
    Load Power Platform data from stdin or environment variable (when run via PowerShell script).
    Returns dict with Power Platform data in the same structure as API client, or None if not available.
    """
    data_source = os.environ.get("POWER_PLATFORM_DATA_SOURCE")
    
    if data_source == "stdin":
        # Data coming from stdin (piped from PowerShell)
        try:
            json_data = sys.stdin.read()
            raw_data = json.loads(json_data)
        except Exception as e:
            print(f"[{get_timestamp()}] ⚠️  Failed to load Power Platform data from stdin: {e}")
            return None
    
    elif data_source == "subprocess":
        # Data passed via environment variable (Python subprocess invoked PowerShell)
        try:
            json_data = os.environ.get("POWER_PLATFORM_DATA_JSON")
            if json_data:
                raw_data = json.loads(json_data)
            else:
                print(f"[{get_timestamp()}] ⚠️  POWER_PLATFORM_DATA_JSON environment variable is empty")
                return None
        except Exception as e:
            print(f"[{get_timestamp()}] ⚠️  Failed to load Power Platform data from environment: {e}")
            return None
    
    else:
        # No data source specified - will use service principal auth instead
        return None
    
    # Transform raw PowerShell data into client-compatible structure
    # Create a simple object to attach attributes to (mimics the httpx client structure)
    class PowerPlatformData:
        pass
    
    client = PowerPlatformData()
    
    # Attach raw data
    client.environments = raw_data.get('environments', [])
    client.flows = raw_data.get('flows', [])
    client.apps = raw_data.get('apps', [])
    client.connections = raw_data.get('connections', [])
    client.ai_models = raw_data.get('ai_models', [])
    client.dlp_policies = raw_data.get('dlp_policies', [])
    client.solutions = raw_data.get('solutions', [])
    
    # Build environment summary
    client.environment_summary = {
        'total': len(client.environments),
        'production': [],
        'sandbox': [],
        'developer': [],
        'default': [],
        'trial': [],
        'other': [],
        'by_state': {'ready': 0, 'preparing': 0, 'disabled': 0, 'other': 0}
    }
    
    for env in client.environments:
        env_name = env.get('name', 'Unknown')
        env_type = env.get('properties', {}).get('environmentType', '').lower()
        env_state = env.get('properties', {}).get('states', {}).get('management', {}).get('id', 'unknown').lower()
        
        env_info = {
            'name': env_name,
            'display_name': env.get('properties', {}).get('displayName', env_name),
            'type': env_type,
            'state': env_state
        }
        
        if 'production' in env_type:
            client.environment_summary['production'].append(env_info)
        elif 'sandbox' in env_type:
            client.environment_summary['sandbox'].append(env_info)
        elif 'developer' in env_type or 'dev' in env_type:
            client.environment_summary['developer'].append(env_info)
        elif 'default' in env_type:
            client.environment_summary['default'].append(env_info)
        elif 'trial' in env_type:
            client.environment_summary['trial'].append(env_info)
        else:
            client.environment_summary['other'].append(env_info)
        
        if 'ready' in env_state:
            client.environment_summary['by_state']['ready'] += 1
        elif 'preparing' in env_state:
            client.environment_summary['by_state']['preparing'] += 1
        elif 'disabled' in env_state:
            client.environment_summary['by_state']['disabled'] += 1
        else:
            client.environment_summary['by_state']['other'] += 1
    
    # Build flow summary
    client.flow_summary = {
        'total': len(client.flows),
        'cloud_flows': [],
        'desktop_flows': [],
        'with_premium_connectors': [],
        'with_http_trigger': [],
        'suspended': [],
        'enabled': 0
    }
    
    for flow in client.flows:
        flow_name = flow.get('name', 'Unknown')
        flow_type = flow.get('properties', {}).get('flowType', '').lower()
        flow_state = flow.get('properties', {}).get('state', '').lower()
        
        if 'desktop' in flow_type or 'rpa' in flow_type:
            client.flow_summary['desktop_flows'].append(flow_name)
        else:
            client.flow_summary['cloud_flows'].append(flow_name)
        
        trigger_type = flow.get('properties', {}).get('definitionSummary', {}).get('triggers', [{}])[0].get('type', '')
        if 'http' in trigger_type.lower() or 'request' in trigger_type.lower():
            client.flow_summary['with_http_trigger'].append(flow_name)
        
        if 'suspended' in flow_state or 'stopped' in flow_state:
            client.flow_summary['suspended'].append(flow_name)
        elif 'started' in flow_state or 'running' in flow_state:
            client.flow_summary['enabled'] += 1
    
    # Build app summary
    client.app_summary = {
        'total': len(client.apps),
        'canvas_apps': [],
        'model_driven_apps': [],
        'teams_apps': [],
        'with_copilot_control': [],
        'sharepoint_connected': []
    }
    
    for app in client.apps:
        app_name = app.get('name', 'Unknown')
        app_type = app.get('properties', {}).get('appType', '').lower()
        
        if 'canvas' in app_type:
            client.app_summary['canvas_apps'].append(app_name)
        elif 'model' in app_type:
            client.app_summary['model_driven_apps'].append(app_name)
        
        if 'teams' in app.get('properties', {}).get('embeddedApp', {}).get('type', '').lower():
            client.app_summary['teams_apps'].append(app_name)
    
    # Build connection summary  
    client.connection_summary = {
        'total': len(client.connections),
        'premium_connectors': [],
        'custom_connectors': [],
        'standard_connectors': [],
        'sap': False,
        'salesforce': False,
        'servicenow': False,
        'sql': False
    }
    
    for connection in client.connections:
        conn_name = connection.get('name', 'Unknown')
        api_id = connection.get('properties', {}).get('apiId', '').lower()
        is_custom = connection.get('properties', {}).get('statuses', [{}])[0].get('status', '') == 'Custom'
        
        if is_custom:
            client.connection_summary['custom_connectors'].append(conn_name)
        elif 'premium' in api_id or 'sql' in api_id or 'sap' in api_id:
            client.connection_summary['premium_connectors'].append(conn_name)
        else:
            client.connection_summary['standard_connectors'].append(conn_name)
        
        if 'sap' in api_id:
            client.connection_summary['sap'] = True
        if 'salesforce' in api_id:
            client.connection_summary['salesforce'] = True
        if 'servicenow' in api_id:
            client.connection_summary['servicenow'] = True
        if 'sql' in api_id:
            client.connection_summary['sql'] = True
    
    # Build AI model summary
    client.ai_model_summary = {
        'total': len(client.ai_models),
        'ai_builder': 0,
        'azure_ml': 0,
        'custom': 0
    }
    
    for model in client.ai_models:
        model_type = model.get('properties', {}).get('modelType', '').lower()
        if 'aibuilder' in model_type:
            client.ai_model_summary['ai_builder'] += 1
        elif 'azureml' in model_type:
            client.ai_model_summary['azure_ml'] += 1
        else:
            client.ai_model_summary['custom'] += 1
    
    # Build DLP summary
    client.dlp_summary = {
        'total': len(client.dlp_policies),
        'environment_level': 0,
        'tenant_level': 0
    }
    
    for policy in client.dlp_policies:
        scope = policy.get('properties', {}).get('scope', '').lower()
        if 'environment' in scope:
            client.dlp_summary['environment_level'] += 1
        elif 'tenant' in scope:
            client.dlp_summary['tenant_level'] += 1
    
    # Build solution summary
    client.solution_summary = {
        'total': len(client.solutions),
        'managed': [],
        'unmanaged': [],
        'with_apps': 0,
        'with_flows': 0,
        'with_tables': 0,
        'alm_ready': 0
    }
    
    for solution in client.solutions:
        solution_name = solution.get('uniquename', 'Unknown')
        is_managed = solution.get('ismanaged', False)
        
        if is_managed:
            client.solution_summary['managed'].append(solution_name)
        else:
            client.solution_summary['unmanaged'].append(solution_name)
        
        components = solution.get('properties', {}).get('components', [])
        has_app = any('app' in str(c).lower() for c in components)
        has_flow = any('flow' in str(c).lower() or 'workflow' in str(c).lower() for c in components)
        has_table = any('entity' in str(c).lower() or 'table' in str(c).lower() for c in components)
        
        if has_app:
            client.solution_summary['with_apps'] += 1
        if has_flow:
            client.solution_summary['with_flows'] += 1
        if has_table:
            client.solution_summary['with_tables'] += 1
        
        if is_managed and (has_app or has_flow or has_table):
            client.solution_summary['alm_ready'] += 1
    
    return client


def format_env_id_for_powerplatform_api(env_name):
    """Convert environment name to powerplatform.com format (removes hyphens).
    Example: 'Default-6b6c3ede-aa0d-4268-a46f-96b7621b13a4' -> 'Default6b6c3edeaa0d4268a46f96b7621b13a4'
    """
    return env_name.replace('-', '') if env_name else ''

async def get_power_platform_client(tenant_id):
    """
    Get authenticated HTTP client for Power Platform Management API.
    Uses shared credential from get_graph_client to avoid multiple auth prompts.
    
    Args:
        tenant_id: Azure tenant ID (GUID or domain name)
    
    Returns:
        Dict with Power Platform data (from PowerShell or API), or None if unavailable
    """
    # Check if data already loaded from PowerShell (via stdin or subprocess)
    preloaded_data = load_power_platform_data_from_stdin()
    if preloaded_data:
        # Data already loaded - return silently (orchestrator handles progress display)
        return preloaded_data
    
    # No preloaded data - fall back to service principal API calls
    try:
        # Import and get Power Platform credential (prefers CLI, falls back to browser)
        from get_graph_client import get_power_platform_credential
        print(f"[DEBUG] Getting Power Platform credential...")
        credential = get_power_platform_credential()  # NOT async - remove await
        print(f"[DEBUG] Credential obtained: {type(credential)}")
        
        # Get tokens for both BAP and Flow APIs (they require different scopes)
        try:
            print(f"[DEBUG] Requesting BAP token for scope: {POWER_PLATFORM_SCOPE}")
            bap_token_response = credential.get_token(POWER_PLATFORM_SCOPE)
            print(f"[DEBUG] BAP token acquired successfully")
            
            print(f"[DEBUG] Requesting Flow token for scope: {FLOW_API_SCOPE}")
            flow_token_response = credential.get_token(FLOW_API_SCOPE)
            print(f"[DEBUG] Flow token acquired successfully")
        except Exception as token_error:
            # Service principal may not have Power Platform API permissions
            print(f"[{get_timestamp()}] ⚠️  Power Platform token acquisition failed: {token_error}")
            print(f"[{get_timestamp()}] ℹ️  Power Platform APIs require delegated permissions (interactive user auth)")
            print(f"[{get_timestamp()}] ℹ️  Service principals need 'Power Platform Administrator' role assigned")
            import traceback
            traceback.print_exc()
            return None
        
        # Create HTTP client with BAP bearer token
        client = httpx.AsyncClient(
            base_url=POWER_PLATFORM_API_BASE,
            headers={
                "Authorization": f"Bearer {bap_token_response.token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30.0  # Increased for reliability with actual environment names
        )
        
        # Create separate client for Flow API with Flow token
        flow_client = httpx.AsyncClient(
            base_url=FLOW_API_BASE,
            headers={
                "Authorization": f"Bearer {flow_token_response.token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        # Fetch environments first to get actual environment name
        # Then use that environment name for all subsequent API calls
        try:
            print(f"[DEBUG] Fetching Power Platform environments...")
            env_response = await client.get(
                "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments",
                params={"api-version": "2023-06-01"}
            )
            print(f"[DEBUG] Environment response status: {env_response.status_code}")
        except Exception as e:
            print(f"[DEBUG] Environment fetch failed: {e}")
            await client.aclose()
            await flow_client.aclose()
            return None
        
        # Check if environments fetch succeeded (required for client to work)
        if env_response.status_code != 200:
            print(f"[DEBUG] Non-200 status code: {env_response.status_code}")
            if env_response.status_code == 403:
                # User doesn't have Power Platform Admin access
                print(f"[{get_timestamp()}] ⚠️  403 Forbidden - Service principal lacks Power Platform Admin permissions")
                print(f"[{get_timestamp()}] ℹ️  Response: {env_response.text[:200]}")
                await client.aclose()
                await flow_client.aclose()
                return None
            else:
                # Other error - close clients and return None
                print(f"[{get_timestamp()}] ⚠️  Power Platform API error {env_response.status_code}")
                print(f"[{get_timestamp()}] ℹ️  Response: {env_response.text[:200]}")
                await client.aclose()
                await flow_client.aclose()
                return None
        
        # Process environments (required)
        environments = env_response.json().get('value', [])
        
        # Get the first available environment name (prefer default, then production, then any)
        environment_name = None
        if environments:
            # Try to find default environment first
            for env in environments:
                env_type = env.get('properties', {}).get('environmentType', '').lower()
                if 'default' in env_type:
                    environment_name = env.get('name')
                    break
            
            # If no default, use first production environment
            if not environment_name:
                for env in environments:
                    env_type = env.get('properties', {}).get('environmentType', '').lower()
                    if 'production' in env_type:
                        environment_name = env.get('name')
                        break
            
            # If still no environment, use first available
            if not environment_name:
                environment_name = environments[0].get('name')
        
        # Store environment name in client for features to use
        client.environment_name = environment_name if environment_name else 'unknown'
        
        # Now fetch other resources using actual environment name
        if environment_name:
            # Power Platform APIs are split across different base URLs:
            # - api.flow.microsoft.com for flows (uses beta admin endpoint)
            # - api.powerplatform.com for apps (uses environment subdomain)
            # - api.bap.microsoft.com for connectors, DLP, AI models (client base URL)
            
            from spinner import _stdout_lock
            with _stdout_lock:
                print(f"[{get_timestamp()}] ℹ️  Fetching Power Platform deployment data...")
                print(f"[{get_timestamp()}] [INFO]     Power Platform: Requesting 7 resource datasets...")
            
            # Format environment ID for powerplatform.com (removes hyphens)
            env_id_for_apps = format_env_id_for_powerplatform_api(environment_name)
            
            api_tasks = {
                'flows': flow_client.get(
                    f"/providers/Microsoft.ProcessSimple/scopes/admin/environments/{environment_name}/v2/flows?api-version=2016-11-01-beta"
                ),
                'apps': client.get(
                    f"https://{env_id_for_apps}.environment.api.powerplatform.com/powerapps/apps?api-version=1"
                ),
                'connections': client.get(
                    f"/providers/Microsoft.PowerApps/scopes/admin/environments/{environment_name}/connections",
                    params={"api-version": "2016-11-01"}
                ),
                'ai_models': client.get(
                    f"/providers/Microsoft.PowerApps/environments/{environment_name}/aiModels",
                    params={"api-version": "2024-05-01"}
                ),
                'dlp_policies': client.get(
                    f"/providers/Microsoft.BusinessAppPlatform/environments/{environment_name}/dlpPolicies",
                    params={"api-version": "2024-05-01"}
                ),
                'capacity': client.get(
                    f"/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{environment_name}/capacity",
                    params={"api-version": "2020-10-01"}
                ),
                'solutions': client.get(
                    f"/providers/Microsoft.PowerApps/scopes/admin/environments/{environment_name}/solutions",
                    params={"api-version": "2016-11-01"}
                )
            }
            
            # Execute all API calls in parallel
            results = await asyncio.gather(*api_tasks.values(), return_exceptions=True)
            
            responses = dict(zip(api_tasks.keys(), results))
        else:
            # No environment name available - set empty responses
            responses = {}
        
        # Early return if no environments (saves processing time)
        if not environments:
            client.environments = []
            client.environment_summary = {'total': 0, 'note': 'No environments found'}
            # Set empty summaries for all resources
            client.flows = []
            client.flow_summary = {'total': 0}
            client.apps = []
            client.app_summary = {'total': 0}
            client.connections = []
            client.connection_summary = {'total': 0}
            client.ai_models = []
            client.ai_model_summary = {'total': 0}
            client.dlp_policies = []
            client.dlp_summary = {'total': 0}
            client.capacity = {}
            client.capacity_summary = {'total': 0}
            client.solutions = []
            client.solution_summary = {'total': 0}
            return client
        
        # Attach raw environment data and parsed metadata to client
        client.environments = environments
        
        # Parse and categorize environments for easier consumption
        client.environment_summary = {
            'total': len(environments),
            'production': [],
            'sandbox': [],
            'developer': [],
            'default': [],
            'trial': [],
            'other': [],
            'by_state': {'ready': 0, 'preparing': 0, 'disabled': 0, 'other': 0}
        }
        
        for env in environments:
            env_name = env.get('name', 'Unknown')
            env_type = env.get('properties', {}).get('environmentType', '').lower()
            env_state = env.get('properties', {}).get('states', {}).get('management', {}).get('id', 'unknown').lower()
            
            # Categorize by type
            env_info = {
                'name': env_name,
                'display_name': env.get('properties', {}).get('displayName', env_name),
                'type': env_type,
                'state': env_state
            }
            
            if 'production' in env_type:
                client.environment_summary['production'].append(env_info)
            elif 'sandbox' in env_type:
                client.environment_summary['sandbox'].append(env_info)
            elif 'developer' in env_type or 'dev' in env_type:
                client.environment_summary['developer'].append(env_info)
            elif 'default' in env_type:
                client.environment_summary['default'].append(env_info)
            elif 'trial' in env_type:
                client.environment_summary['trial'].append(env_info)
            else:
                client.environment_summary['other'].append(env_info)
            
            # Track states
            if 'ready' in env_state:
                client.environment_summary['by_state']['ready'] += 1
            elif 'preparing' in env_state:
                client.environment_summary['by_state']['preparing'] += 1
            elif 'disabled' in env_state:
                client.environment_summary['by_state']['disabled'] += 1
            else:
                client.environment_summary['by_state']['other'] += 1
        
        # Process flows (optional - may fail if no access)
        flows_response = responses.get('flows')
        if not isinstance(flows_response, Exception) and flows_response.status_code == 200:
            flows = flows_response.json().get('value', [])
            client.flows = flows
            
            # Categorize flows for Copilot adoption insights
            client.flow_summary = {
                'total': len(flows),
                'cloud_flows': [],
                'desktop_flows': [],
                'with_premium_connectors': [],
                'with_http_trigger': [],
                'suspended': [],
                'enabled': 0
            }
            
            for flow in flows:
                flow_name = flow.get('name', 'Unknown')
                flow_type = flow.get('properties', {}).get('flowType', '').lower()
                flow_state = flow.get('properties', {}).get('state', '').lower()
                
                # Track cloud vs desktop flows
                if 'desktop' in flow_type or 'rpa' in flow_type:
                    client.flow_summary['desktop_flows'].append(flow_name)
                else:
                    client.flow_summary['cloud_flows'].append(flow_name)
                
                # Check for HTTP triggers (Copilot plugin candidates)
                trigger_type = flow.get('properties', {}).get('definitionSummary', {}).get('triggers', [{}])[0].get('type', '')
                if 'http' in trigger_type.lower() or 'request' in trigger_type.lower():
                    client.flow_summary['with_http_trigger'].append(flow_name)
                
                # Track state
                if 'suspended' in flow_state or 'stopped' in flow_state:
                    client.flow_summary['suspended'].append(flow_name)
                elif 'started' in flow_state or 'running' in flow_state:
                    client.flow_summary['enabled'] += 1
        else:
            client.flows = []
            error_detail = f"Status: {flows_response.status_code}" if not isinstance(flows_response, Exception) else str(flows_response)
            client.flow_summary = {'total': 0, 'error': f'Unable to fetch flows - {error_detail}'}
        
        # Process apps (optional)
        apps_response = responses.get('apps')
        if not isinstance(apps_response, Exception) and apps_response.status_code == 200:
            apps = apps_response.json().get('value', [])
            client.apps = apps
            
            # Categorize apps for Copilot integration insights
            client.app_summary = {
                'total': len(apps),
                'canvas_apps': [],
                'model_driven_apps': [],
                'teams_apps': [],
                'with_copilot_control': [],
                'sharepoint_connected': []
            }
            
            for app in apps:
                app_name = app.get('name', 'Unknown')
                app_type = app.get('properties', {}).get('appType', '').lower()
                
                # Categorize by type
                if 'canvas' in app_type:
                    client.app_summary['canvas_apps'].append(app_name)
                elif 'model' in app_type or 'driven' in app_type:
                    client.app_summary['model_driven_apps'].append(app_name)
                
                # Check for Teams integration
                app_context = app.get('properties', {}).get('appOpenProtocolUri', '')
                if 'teams' in app_context.lower():
                    client.app_summary['teams_apps'].append(app_name)
        else:
            client.apps = []
            error_detail = f"Status: {apps_response.status_code}" if not isinstance(apps_response, Exception) else str(apps_response)
            client.app_summary = {'total': 0, 'error': f'Unable to fetch apps - {error_detail}'}
        
        # Process connections (optional)
        connections_response = responses.get('connections')
        if not isinstance(connections_response, Exception) and connections_response.status_code == 200:
            connections = connections_response.json().get('value', [])
            client.connections = connections
            
            # Categorize connectors for extensibility insights
            client.connection_summary = {
                'total': len(connections),
                'premium_connectors': set(),
                'standard_connectors': set(),
                'custom_connectors': [],
                'sap': False,
                'salesforce': False,
                'servicenow': False,
                'sql': False
            }
            
            # Premium connector list (subset - key ones for Copilot extensibility)
            premium_list = ['sap', 'salesforce', 'servicenow', 'dynamics', 'oracle', 'http', 'custom']
            
            for conn in connections:
                conn_type = conn.get('properties', {}).get('apiId', '').lower()
                conn_name = conn.get('name', '')
                
                # Check if premium
                is_premium = any(p in conn_type for p in premium_list)
                if is_premium:
                    client.connection_summary['premium_connectors'].add(conn_type)
                else:
                    client.connection_summary['standard_connectors'].add(conn_type)
                
                # Flag key enterprise connectors
                if 'sap' in conn_type:
                    client.connection_summary['sap'] = True
                if 'salesforce' in conn_type:
                    client.connection_summary['salesforce'] = True
                if 'servicenow' in conn_type:
                    client.connection_summary['servicenow'] = True
                if 'sql' in conn_type:
                    client.connection_summary['sql'] = True
                if 'custom' in conn_type:
                    client.connection_summary['custom_connectors'].append(conn_name)
            
            # Convert sets to counts
            client.connection_summary['premium_connectors'] = list(client.connection_summary['premium_connectors'])
            client.connection_summary['standard_connectors'] = list(client.connection_summary['standard_connectors'])
        else:
            client.connections = []
            client.connection_summary = {'total': 0, 'error': 'Unable to fetch connections'}
        
        # Phase 2: Process AI Builder models (optional)
        ai_models_response = responses.get('ai_models')
        if not isinstance(ai_models_response, Exception) and ai_models_response and ai_models_response.status_code == 200:
            ai_models = ai_models_response.json().get('value', [])
            client.ai_models = ai_models
            
            # Categorize AI Builder models by type
            client.ai_model_summary = {
                'total': len(ai_models),
                'document_processing': [],
                'prediction': [],
                'object_detection': [],
                'text_classification': [],
                'form_processing': [],
                'entity_extraction': [],
                'trained_models': 0,
                'published_models': 0
            }
            
            for model in ai_models:
                model_name = model.get('name', 'Unknown')
                model_type = model.get('properties', {}).get('modelType', '').lower()
                model_status = model.get('properties', {}).get('status', '').lower()
                
                # Categorize by type
                if 'document' in model_type or 'invoice' in model_type or 'receipt' in model_type:
                    client.ai_model_summary['document_processing'].append(model_name)
                elif 'prediction' in model_type or 'forecast' in model_type:
                    client.ai_model_summary['prediction'].append(model_name)
                elif 'object' in model_type or 'detection' in model_type:
                    client.ai_model_summary['object_detection'].append(model_name)
                elif 'text' in model_type or 'classification' in model_type or 'sentiment' in model_type:
                    client.ai_model_summary['text_classification'].append(model_name)
                elif 'form' in model_type:
                    client.ai_model_summary['form_processing'].append(model_name)
                elif 'entity' in model_type or 'extraction' in model_type:
                    client.ai_model_summary['entity_extraction'].append(model_name)
                
                # Track training/publishing status
                if 'trained' in model_status or 'ready' in model_status:
                    client.ai_model_summary['trained_models'] += 1
                if 'published' in model_status:
                    client.ai_model_summary['published_models'] += 1
        else:
            client.ai_models = []
            error_detail = f"Status: {ai_models_response.status_code}" if not isinstance(ai_models_response, Exception) else str(ai_models_response)
            client.ai_model_summary = {'total': 0, 'error': f'Unable to fetch AI Builder models - {error_detail}'}
        
        # Phase 2: Process DLP policies (optional)
        dlp_response = responses.get('dlp_policies')
        if not isinstance(dlp_response, Exception) and dlp_response.status_code == 200:
            dlp_policies = dlp_response.json().get('value', [])
            client.dlp_policies = dlp_policies
            
            # Analyze DLP policies for Copilot extensibility blockers
            client.dlp_summary = {
                'total': len(dlp_policies),
                'blocks_http': False,
                'blocks_custom_connectors': False,
                'blocks_premium': False,
                'restricted_connectors': [],
                'tenant_wide_policies': 0,
                'environment_specific': 0
            }
            
            for policy in dlp_policies:
                policy_scope = policy.get('properties', {}).get('scope', '').lower()
                connector_groups = policy.get('properties', {}).get('connectorGroups', {})
                
                # Check scope
                if 'tenant' in policy_scope or policy_scope == '/':
                    client.dlp_summary['tenant_wide_policies'] += 1
                else:
                    client.dlp_summary['environment_specific'] += 1
                
                # Check for blocked connectors (in "Blocked" group)
                blocked_connectors = connector_groups.get('hbi', {}).get('classification', []) if 'hbi' in connector_groups else []
                
                for conn in blocked_connectors:
                    conn_id = conn.get('id', '').lower()
                    
                    # Flag key blockers for Copilot extensibility
                    if 'http' in conn_id:
                        client.dlp_summary['blocks_http'] = True
                        client.dlp_summary['restricted_connectors'].append('HTTP')
                    if 'custom' in conn_id:
                        client.dlp_summary['blocks_custom_connectors'] = True
                        client.dlp_summary['restricted_connectors'].append('Custom Connectors')
                    if any(p in conn_id for p in ['premium', 'salesforce', 'sap', 'servicenow']):
                        client.dlp_summary['blocks_premium'] = True
        else:
            client.dlp_policies = []
            error_detail = f"Status: {dlp_response.status_code}" if not isinstance(dlp_response, Exception) else str(dlp_response)
            client.dlp_summary = {'total': 0, 'error': f'Unable to fetch DLP policies - {error_detail}'}
        
        # Phase 2: Process Dataverse capacity (optional)
        capacity_response = responses.get('capacity')
        if not isinstance(capacity_response, Exception) and capacity_response.status_code == 200:
            capacity_data = capacity_response.json()
            client.capacity = capacity_data
            
            # Analyze capacity for agent scalability
            storage = capacity_data.get('storage', {})
            client.capacity_summary = {
                'available': True,
                'database_capacity_mb': storage.get('databaseCapacity', 0),
                'database_used_mb': storage.get('databaseUsed', 0),
                'file_capacity_mb': storage.get('fileCapacity', 0),
                'file_used_mb': storage.get('fileUsed', 0),
                'log_capacity_mb': storage.get('logCapacity', 0),
                'log_used_mb': storage.get('logUsed', 0)
            }
            
            # Calculate usage percentages
            db_capacity = client.capacity_summary['database_capacity_mb']
            db_used = client.capacity_summary['database_used_mb']
            if db_capacity > 0:
                client.capacity_summary['database_usage_percent'] = int((db_used / db_capacity) * 100)
            else:
                client.capacity_summary['database_usage_percent'] = 0
            
            file_capacity = client.capacity_summary['file_capacity_mb']
            file_used = client.capacity_summary['file_used_mb']
            if file_capacity > 0:
                client.capacity_summary['file_usage_percent'] = int((file_used / file_capacity) * 100)
            else:
                client.capacity_summary['file_usage_percent'] = 0
        else:
            client.capacity = {}
            client.capacity_summary = {'available': False, 'error': 'Unable to fetch capacity data'}
        
        # Phase 3: Process Solutions (optional)
        solutions_response = responses.get('solutions')
        if not isinstance(solutions_response, Exception) and solutions_response and solutions_response.status_code == 200:
            solutions = solutions_response.json().get('value', [])
            client.solutions = solutions
            
            # Analyze solutions for ALM maturity
            client.solution_summary = {
                'total': len(solutions),
                'managed': [],
                'unmanaged': [],
                'with_apps': 0,
                'with_flows': 0,
                'with_tables': 0,
                'alm_ready': 0
            }
            
            for solution in solutions:
                solution_name = solution.get('uniquename', 'Unknown')
                is_managed = solution.get('ismanaged', False)
                
                # Track managed vs unmanaged
                if is_managed:
                    client.solution_summary['managed'].append(solution_name)
                else:
                    client.solution_summary['unmanaged'].append(solution_name)
                
                # Check for components (indicates solution usage)
                components = solution.get('properties', {}).get('components', [])
                has_app = any('app' in str(c).lower() for c in components)
                has_flow = any('flow' in str(c).lower() or 'workflow' in str(c).lower() for c in components)
                has_table = any('entity' in str(c).lower() or 'table' in str(c).lower() for c in components)
                
                if has_app:
                    client.solution_summary['with_apps'] += 1
                if has_flow:
                    client.solution_summary['with_flows'] += 1
                if has_table:
                    client.solution_summary['with_tables'] += 1
                
                # Consider solution ALM-ready if it's managed and has components
                if is_managed and (has_app or has_flow or has_table):
                    client.solution_summary['alm_ready'] += 1
        else:
            client.solutions = []
            client.solution_summary = {'total': 0, 'error': 'Unable to fetch solutions'}
        
        return client
            
    except Exception as e:
        # Authentication or other error - return None
        return None


def extract_pp_insights_from_client(pp_client):
    """
    Extract Power Platform deployment insights from cached client data.
    Call this ONCE and reuse the result across all recommendations to avoid redundant processing.
    
    Returns:
        dict with flows, apps, connections, AI models, environments metadata
    """
    if not pp_client:
        return {
            'flows_total': 0,
            'cloud_flows': 0,
            'desktop_flows': 0,
            'http_triggers': 0,
            'suspended_flows': 0,
            'apps_total': 0,
            'canvas_apps': 0,
            'model_driven_apps': 0,
            'teams_apps': 0,
            'connections_total': 0,
            'premium_connectors': 0,
            'custom_connectors': 0,
            'has_sap': False,
            'has_salesforce': False,
            'has_servicenow': False,
            'has_sql': False,
            'ai_models_total': 0,
            'environments_total': 0,
            'production_envs': 0,
            'sandbox_envs': 0,
            'trial_envs': 0
        }
    
    # Extract from pre-computed summaries (no API calls - already cached!)
    flow_summary = getattr(pp_client, 'flow_summary', {})
    app_summary = getattr(pp_client, 'app_summary', {})
    connection_summary = getattr(pp_client, 'connection_summary', {})
    ai_model_summary = getattr(pp_client, 'ai_model_summary', {})
    env_summary = getattr(pp_client, 'environment_summary', {})
    
    return {
        # Flows
        'flows_total': flow_summary.get('total', 0),
        'cloud_flows': len(flow_summary.get('cloud_flows', [])),
        'desktop_flows': len(flow_summary.get('desktop_flows', [])),
        'http_triggers': len(flow_summary.get('with_http_trigger', [])),
        'suspended_flows': len(flow_summary.get('suspended', [])),
        
        # Apps
        'apps_total': app_summary.get('total', 0),
        'canvas_apps': len(app_summary.get('canvas_apps', [])),
        'model_driven_apps': len(app_summary.get('model_driven_apps', [])),
        'teams_apps': len(app_summary.get('teams_apps', [])),
        
        # Connections
        'connections_total': connection_summary.get('total', 0),
        'premium_connectors': len(connection_summary.get('premium_connectors', [])),
        'custom_connectors': len(connection_summary.get('custom_connectors', [])),
        'has_sap': connection_summary.get('sap', False),
        'has_salesforce': connection_summary.get('salesforce', False),
        'has_servicenow': connection_summary.get('servicenow', False),
        'has_sql': connection_summary.get('sql', False),
        
        # AI Models
        'ai_models_total': ai_model_summary.get('total', 0),
        
        # Environments
        'environments_total': env_summary.get('total', 0),
        'production_envs': len(env_summary.get('production', [])),
        'sandbox_envs': len(env_summary.get('sandbox', [])),
        'trial_envs': len(env_summary.get('trial', []))
    }
