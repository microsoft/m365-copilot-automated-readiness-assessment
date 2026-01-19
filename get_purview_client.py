"""
Microsoft Purview/Compliance API Client
Fetches actual deployment data from Purview endpoints

NOTE: Uses PowerShell data collector (collect_purview_data.ps1) to collect data.
The script runs Connect-IPPSSession, collects cmdlet outputs, and pipes JSON to Python via stdin.
No cache files are created - data is passed directly in memory.
"""
import asyncio
import json
import os
import sys
from get_graph_client import get_api_client
from spinner import get_timestamp, _stdout_lock


# Global variable to store PowerShell data passed via stdin
_PURVIEW_DATA_CACHE = None


def load_purview_data_from_stdin():
    """Load Purview data from stdin (passed by PowerShell wrapper) or subprocess"""
    global _PURVIEW_DATA_CACHE
    
    # Check data source
    data_source = os.environ.get('PURVIEW_DATA_SOURCE')
    if data_source not in ('stdin', 'subprocess'):
        return None
    
    # Return cached data if already loaded
    if _PURVIEW_DATA_CACHE is not None:
        return _PURVIEW_DATA_CACHE
    
    # Load from subprocess JSON environment variable
    if data_source == 'subprocess':
        try:
            json_data = os.environ.get('PURVIEW_DATA_JSON')
            if json_data:
                _PURVIEW_DATA_CACHE = json.loads(json_data)
                return _PURVIEW_DATA_CACHE
        except Exception as e:
            print(f"[{get_timestamp()}] ⚠️ Failed to load Purview data from subprocess: {e}")
            import traceback
            traceback.print_exc()
        return None
    
    # Load from stdin
    try:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                _PURVIEW_DATA_CACHE = json.loads(stdin_data)
                # Data loaded silently - progress managed by orchestrator
                return _PURVIEW_DATA_CACHE
    except Exception as e:
        print(f"[{get_timestamp()}] ⚠️ Failed to load Purview data from stdin: {e}")
        import traceback
        traceback.print_exc()
    
    return None


async def get_purview_client(tenant_id):
    """
    Create Purview client and fetch deployment data from PowerShell stdin.
    
    Data flow:
    - Run: .\collect_purview_data.ps1 (connects to PowerShell, collects data, pipes to Python)
    - Data passed via stdin - no cache files created
    - All data available in single JSON structure
    
    Args:
        tenant_id: Azure tenant ID (GUID or domain name)
    
    Returns:
        Object with deployment data hydrated from PowerShell cmdlet outputs
    """
    # Note: Graph HTTP client not currently used (Purview data comes from PowerShell)
    # but kept for potential future Graph API integration (e.g., audit logs, license checks)
    graph_http = None
    
    # Load data from PowerShell stdin (no HTTP client needed - uses PowerShell cmdlets)
    purview_data = load_purview_data_from_stdin()
    
    # Helper to safely extract nested data
    def safe_get(data, key, nested_key=None):
        """Safely extract data, handling cases where PowerShell JSON structure varies"""
        if not isinstance(data, dict):
            return [] if nested_key else {}
        value = data.get(key, {})
        if not isinstance(value, dict):
            return [] if nested_key else {}
        if nested_key:
            result = value.get(nested_key, [])
            return result if isinstance(result, list) else []
        return value
    
    # Extract data from PowerShell output
    if purview_data:
        dlp_data = safe_get(purview_data, 'dlp_policies', 'policies')
        labels_data = safe_get(purview_data, 'sensitivity_labels', 'labels')
        retention_data = safe_get(purview_data, 'retention_policies', 'policies')
        label_policies_data = safe_get(purview_data, 'label_policies', 'policies')
        insider_risk_data = safe_get(purview_data, 'insider_risk_policies', 'policies')
        comm_comp_data = safe_get(purview_data, 'communication_compliance', 'policies')
        ib_data = safe_get(purview_data, 'information_barriers', 'policies')
        ediscovery_data = safe_get(purview_data, 'ediscovery_cases', 'cases')
        org_config_data = safe_get(purview_data, 'org_config')
        irm_config_data = safe_get(purview_data, 'irm_config')
        audit_config_data = safe_get(purview_data, 'audit_config')
    else:
        print(f"[{get_timestamp()}] ℹ️  No Purview data provided. Run: .\\collect_purview_data.ps1 for deployment-specific recommendations")
        dlp_data = labels_data = retention_data = label_policies_data = []
        insider_risk_data = comm_comp_data = ib_data = ediscovery_data = []
        org_config_data = irm_config_data = audit_config_data = {}
    
    # Fetch data from all endpoints in parallel
    async def fetch_retention_labels():
        if retention_data:
            return {
                'available': True, 
                'total_labels': len(retention_data) if isinstance(retention_data, list) else 0,
                'labels': retention_data
            }
        return {'available': False, 'total_labels': 0}
    
    async def fetch_sensitivity_labels():
        if labels_data:
            return {
                'available': True,
                'total_labels': len(labels_data) if isinstance(labels_data, list) else 0,
                'labels': labels_data
            }
        return {'available': False, 'total_labels': 0}
    
    async def fetch_label_policies():
        if label_policies_data:
            return {
                'available': True,
                'total_policies': len(label_policies_data) if isinstance(label_policies_data, list) else 0,
                'policies': label_policies_data
            }
        return {'available': False, 'total_policies': 0}
    
    async def fetch_retention_events():
        return {'available': False, 'total_events': 0}
    
    async def fetch_retention_event_types():
        return {'available': False, 'total_types': 0}
    
    async def fetch_information_barriers():
        if ib_data:
            return {
                'available': True,
                'total_policies': len(ib_data) if isinstance(ib_data, list) else 0,
                'policies': ib_data
            }
        return {'available': False, 'total_policies': 0}
    
    async def fetch_ediscovery_cases():
        if ediscovery_data:
            active_count = sum(1 for c in ediscovery_data if c.get('Status') == 'Active')
            return {
                'available': True,
                'total_cases': len(ediscovery_data),
                'active_cases': active_count,
                'cases': ediscovery_data
            }
        return {'available': False, 'total_cases': 0, 'active_cases': 0}
    
    async def fetch_dlp_policies():
        if dlp_data:
            enabled_count = sum(1 for p in dlp_data if p.get('Enabled'))
            return {
                'available': True,
                'total_policies': len(dlp_data),
                'enabled_policies': enabled_count,
                'policies': dlp_data
            }
        return {'available': False, 'total_policies': 0}
    
    async def fetch_dlp_alerts():
        return {'available': False, 'total_alerts': 0}
    
    async def fetch_irm_alerts():
        return {'available': False, 'total_alerts': 0}
    
    async def fetch_insider_risk():
        if insider_risk_data:
            return {
                'available': True,
                'total_policies': len(insider_risk_data),
                'policies': insider_risk_data
            }
        return {'available': False, 'total_policies': 0}
    
    async def fetch_comm_compliance():
        if comm_comp_data:
            return {
                'available': True,
                'total_policies': len(comm_comp_data),
                'policies': comm_comp_data
            }
        return {'available': False, 'total_policies': 0}
    
    async def fetch_org_config():
        if org_config_data:
            return {
                'available': True,
                'customer_lockbox_enabled': org_config_data.get('CustomerLockBoxEnabled', False),
                'audit_disabled': org_config_data.get('AuditDisabled', False)
            }
        return {'available': False}
    
    async def fetch_irm_config():
        if irm_config_data:
            return {
                'available': True,
                'azure_rms_enabled': irm_config_data.get('AzureRMSLicensingEnabled', False)
            }
        return {'available': False}
    
    async def fetch_audit_config():
        if audit_config_data:
            return {
                'available': True,
                'unified_audit_enabled': audit_config_data.get('UnifiedAuditLogIngestionEnabled', False),
                'admin_audit_enabled': audit_config_data.get('AdminAuditLogEnabled', False)
            }
        return {'available': False}
    
    async def fetch_audit_logs():
        # Audit logs come from PowerShell data, not Graph API
        # (Graph audit logs API is separate and not part of Purview)
        return {'available': False, 'recent_count': 0}
    
    async def fetch_customer_lockbox():
        return {'available': False, 'total_requests': 0}
    
    # Run all fetches in parallel (progress managed by orchestrator)
    try:
        results = await asyncio.gather(
            fetch_sensitivity_labels(),
            fetch_retention_labels(),
            fetch_label_policies(),
            fetch_retention_events(),
            fetch_retention_event_types(),
            fetch_information_barriers(),
            fetch_ediscovery_cases(),
            fetch_dlp_policies(),
            fetch_dlp_alerts(),
            fetch_irm_alerts(),
            fetch_insider_risk(),
            fetch_comm_compliance(),
            fetch_org_config(),
            fetch_irm_config(),
            fetch_audit_config(),
            fetch_audit_logs(),
            fetch_customer_lockbox(),
            return_exceptions=True
        )
        
        (sensitivity_labels, retention_labels, label_policies, retention_events, retention_event_types,
         information_barriers, ediscovery_cases, dlp_policies, dlp_alerts,
         irm_alerts, insider_risk, comm_compliance, org_config, irm_config, 
         audit_config, audit_logs, customer_lockbox) = results
        
        # Count available endpoints
        endpoint_results = {
            'Sensitivity Labels': sensitivity_labels,
            'Label Policies': label_policies,
            'Retention Labels': retention_labels,
            'Retention Events': retention_events,
            'Retention Event Types': retention_event_types,
            'Information Barriers': information_barriers,
            'eDiscovery Cases': ediscovery_cases,
            'DLP Policies': dlp_policies,
            'DLP Alerts': dlp_alerts,
            'Insider Risk': insider_risk,
            'Insider Risk Alerts': irm_alerts,
            'Communication Compliance': comm_compliance,
            'Organization Config': org_config,
            'IRM Config': irm_config,
            'Audit Config': audit_config,
            'Audit Logs': audit_logs,
            'Customer Lockbox': customer_lockbox
        }
        
        success_count = sum(1 for result in endpoint_results.values() 
                          if not isinstance(result, Exception) and result.get('available'))
        
    except Exception as e:
        raise Exception(f"Failed to fetch Purview data: {str(e)}")
    
    # Build client object with all deployment data
    class PurviewClient:
        def __init__(self):
            self.sensitivity_labels = sensitivity_labels if not isinstance(sensitivity_labels, Exception) else {'available': False}
            self.label_policies = label_policies if not isinstance(label_policies, Exception) else {'available': False}
            self.retention_labels = retention_labels if not isinstance(retention_labels, Exception) else {'available': False}
            self.retention_events = retention_events if not isinstance(retention_events, Exception) else {'available': False}
            self.retention_event_types = retention_event_types if not isinstance(retention_event_types, Exception) else {'available': False}
            self.information_barriers = information_barriers if not isinstance(information_barriers, Exception) else {'available': False}
            self.ediscovery_cases = ediscovery_cases if not isinstance(ediscovery_cases, Exception) else {'available': False}
            self.dlp_policies = dlp_policies if not isinstance(dlp_policies, Exception) else {'available': False}
            self.dlp_alerts = dlp_alerts if not isinstance(dlp_alerts, Exception) else {'available': False}
            self.insider_risk = insider_risk if not isinstance(insider_risk, Exception) else {'available': False}
            self.irm_alerts = irm_alerts if not isinstance(irm_alerts, Exception) else {'available': False}
            self.comm_compliance = comm_compliance if not isinstance(comm_compliance, Exception) else {'available': False}
            self.org_config = org_config if not isinstance(org_config, Exception) else {'available': False}
            self.irm_config = irm_config if not isinstance(irm_config, Exception) else {'available': False}
            self.audit_config = audit_config if not isinstance(audit_config, Exception) else {'available': False}
            self.audit_logs = audit_logs if not isinstance(audit_logs, Exception) else {'available': False}
            self.customer_lockbox = customer_lockbox if not isinstance(customer_lockbox, Exception) else {'available': False}
            
            # Summary counts
            self.total_endpoints_available = sum([
                self.sensitivity_labels.get('available', False),
                self.label_policies.get('available', False),
                self.retention_labels.get('available', False),
                self.retention_events.get('available', False),
                self.retention_event_types.get('available', False),
                self.information_barriers.get('available', False),
                self.ediscovery_cases.get('available', False),
                self.dlp_policies.get('available', False),
                self.dlp_alerts.get('available', False),
                self.insider_risk.get('available', False),
                self.irm_alerts.get('available', False),
                self.comm_compliance.get('available', False),
                self.org_config.get('available', False),
                self.irm_config.get('available', False),
                self.audit_config.get('available', False),
                self.audit_logs.get('available', False),
                self.customer_lockbox.get('available', False)
            ])
    
    return PurviewClient()

