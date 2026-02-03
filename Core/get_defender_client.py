"""
Microsoft Defender API Client
Provides authenticated access to Microsoft 365 Defender and Graph Security APIs.
Fetches and caches: security alerts, incidents, secure score, devices, vulnerabilities.
Gracefully handles lower SKUs (M365 Basic, Business Standard, Business Premium, E3).
"""
import asyncio
import os
import sys
import json
from azure.identity.aio import AzureCliCredential
from azure.core.exceptions import HttpResponseError
from .spinner import get_timestamp, _stdout_lock

async def get_defender_client(tenant_id, graph_client):
    """
    Get authenticated clients for Microsoft Defender and Graph Security APIs.
    Fetches actual security/threat data to enrich license-based observations.
    
    Supports two modes:
    1. Service Principal (via .env file) - for automation
    2. Delegated Auth (via collect_defender_data.ps1) - bypasses device onboarding requirement
    
    Args:
        tenant_id: Azure tenant ID (GUID or domain name)
        graph_client: Existing Microsoft Graph SDK client (for Graph Security API)
    
    Returns:
        Object with cached security data from both Graph Security and Defender APIs,
        or minimal client if permissions are insufficient (graceful degradation for lower SKUs)
    """
    
    # Check if running with delegated auth data (from PowerShell collector)
    delegated_defender_data = os.getenv('DEFENDER_DATA')
    if delegated_defender_data:
        with _stdout_lock:
            print(f"[{get_timestamp()}] ℹ️  Using Defender data from delegated authentication")
        return await _load_delegated_defender_data(delegated_defender_data, graph_client)
    
    # Otherwise, use service principal mode (existing behavior)
    
    # Create a simple object to store fetched data
    class DefenderClient:
        def __init__(self):
            self.available = False
            self.graph_security_available = False
            self.defender_api_available = False
            
            # Activation status flags
            self.activation_needed = False
            self.activation_message = ""
            
            # Track missing features (404 errors)
            self.missing_features = []  # List of features not available in license
            
            # Graph Security API data
            self.security_alerts = []
            self.alert_summary = {'total': 0, 'by_severity': {}, 'by_category': {}, 'copilot_related': 0}
            
            self.security_incidents = []
            self.incident_summary = {'total': 0, 'active': 0, 'resolved': 0, 'high_severity': 0}
            
            self.secure_score = {}
            self.secure_score_summary = {'current_score': 0, 'max_score': 0, 'percentage': 0}
            
            self.secure_score_controls = []
            self.control_summary = {'total': 0, 'implemented': 0, 'not_implemented': 0}
            
            # Defender API data (more detailed)
            self.defender_incidents = []
            self.defender_incident_summary = {'total': 0, 'in_progress': 0, 'new': 0}
            
            self.defender_devices = []
            self.device_summary = {'total': 0, 'high_risk': 0, 'medium_risk': 0, 'low_risk': 0, 'copilot_enabled': 0}
            
            self.defender_vulnerabilities = []
            self.vulnerability_summary = {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            
            self.advanced_hunting_results = {}
            
            # Identity Protection data (Copilot access risk)
            self.risky_users = []
            self.risky_users_summary = {'total': 0, 'high': 0, 'medium': 0, 'low': 0, 'confirmed_compromised': 0}
            
            self.risky_sign_ins = []
            self.risky_sign_ins_summary = {'total': 0, 'high_risk': 0, 'medium_risk': 0}
            
            # Email Threats data (Copilot content risk)
            self.email_threats = []
            self.email_threat_summary = {'total': 0, 'phishing': 0, 'malware': 0, 'spam': 0}
            
            # Cloud App & OAuth Risks (Agent integration risk)
            self.oauth_apps = []
            self.oauth_risk_summary = {'total_apps': 0, 'high_risk': 0, 'medium_risk': 0, 'over_privileged': 0}
            
            # DLP Incidents (Data leakage via Copilot)
            self.dlp_incidents = []
            self.dlp_incident_summary = {'total': 0, 'high_severity': 0, 'copilot_related': 0}
            
            # Enhanced secure score controls (Identity & Data focused)
            self.identity_controls = []
            self.data_controls = []
            self.control_focus_summary = {'identity_controls': 0, 'data_controls': 0, 'copilot_relevant': 0}
            
            # Advanced Hunting results (Copilot-specific threat intelligence)
            self.copilot_process_events = {}
            self.copilot_network_events = {}
            self.copilot_file_access_events = {}
            self.copilot_email_threats = {}
            self.hunting_summary = {
                'suspicious_processes': 0,
                'unusual_network_activity': 0,
                'sensitive_file_access': 0,
                'phishing_attempts': 0,
                'affected_devices': 0,
                'affected_users': 0
            }
            
            # Security recommendations (configuration gaps)
            self.security_recommendations = []
            self.recommendations_summary = {
                'total': 0,
                'critical': 0,
                'high': 0,
                'copilot_related': 0
            }
            
            # Software inventory (Copilot app detection)
            self.software_inventory = []
            self.software_summary = {
                'total_apps': 0,
                'copilot_apps': 0,
                'vulnerable_apps': 0
            }
            
            # Exposure score (overall security posture)
            self.exposure_score = {}
            self.exposure_summary = {
                'score': 0,
                'level': 'Unknown',
                'trend': 'Unknown'
            }
            
    client = DefenderClient()
    
    # ========== PART 1: Graph Security API (via existing Graph client) ==========
    # More widely available, works with most M365 SKUs
    
    # Track if we've shown tips to avoid repetition
    graph_security_tip_shown = False
    defender_api_tip_shown = False
    
    graph_tasks = {}
    
    try:
        # Note: Graph SDK request_configuration with lambda may have issues
        # Simplified to basic .get() calls - filtering can be added later if needed
        
        # Create async tasks (properly wrapped)
        graph_tasks['alerts'] = asyncio.create_task(graph_client.security.alerts_v2.get())
        graph_tasks['incidents'] = asyncio.create_task(graph_client.security.incidents.get())
        graph_tasks['secure_scores'] = asyncio.create_task(graph_client.security.secure_scores.get())
        graph_tasks['secure_score_controls'] = asyncio.create_task(graph_client.security.secure_score_control_profiles.get())
        
        # Fetch Identity Protection data (risky users who might access Copilot)
        try:
            graph_tasks['risky_users'] = asyncio.create_task(graph_client.identity_protection.risky_users.get())
        except AttributeError:
            # risky_users may not be available in this SDK version
            pass
        
        # Fetch OAuth app consent (third-party apps with risky permissions for Agent integration)
        # Note: This may require additional permissions
        try:
            graph_tasks['oauth_grants'] = asyncio.create_task(graph_client.oauth2_permission_grants.get())
        except:
            pass  # May not have permission, continue without it
        
        # DISABLED: Progress display causes deadlock with ProgressDisplay threading
        # TODO: Fix ProgressDisplay threading or use simpler approach
        total_tasks = len(graph_tasks)
        
        # Execute all Graph Security API calls in parallel using gather (like Power Platform does)
        results = await asyncio.gather(*graph_tasks.values(), return_exceptions=True)
        
        # Process results and match them to task names
        graph_results = {}
        for (key, task), result in zip(graph_tasks.items(), results):
            if isinstance(result, HttpResponseError):
                e = result
                if e.status_code == 403:
                    error_msg = str(e)
                    if 'not provisioned' in error_msg.lower():
                        client.activation_needed = True
                        if not client.activation_message:
                            client.activation_message = "Microsoft Defender XDR not activated"
                    else:
                        with _stdout_lock:
                            print(f"[{get_timestamp()}] ⚠️  Graph Security API ({key}): Insufficient permissions (403)")
                elif e.status_code == 404:
                    with _stdout_lock:
                        print(f"[{get_timestamp()}] ⚠️  Graph Security API ({key}): Not available in current SKU (404)")
                else:
                    with _stdout_lock:
                        print(f"[{get_timestamp()}] ⚠️  Graph Security API ({key}): HTTP {e.status_code}")
                graph_results[key] = None
            elif isinstance(result, Exception):
                error_msg = str(result)
                if 'not provisioned' in error_msg.lower():
                    client.activation_needed = True
                    if not client.activation_message:
                        client.activation_message = "Microsoft Defender XDR not activated"
                else:
                    with _stdout_lock:
                        print(f"[{get_timestamp()}] ⚠️  Graph Security API ({key}): {str(result)[:100]}")
                graph_results[key] = None
            else:
                graph_results[key] = result
                client.graph_security_available = True
        
        # Progress display disabled
        successful = sum(1 for v in graph_results.values() if v is not None)
        with _stdout_lock:
            sys.stdout.write(f"\r[{get_timestamp()}] ✓ Graph Security API: {successful}/{total_tasks} datasets fetched\n")
            sys.stdout.flush()
        
        # Process Graph Security Alerts
        if graph_results.get('alerts'):
            alerts_data = graph_results['alerts']
            if hasattr(alerts_data, 'value') and alerts_data.value:
                client.security_alerts = alerts_data.value
                
                # Build alert summary
                client.alert_summary['total'] = len(alerts_data.value)
                severity_counts = {}
                category_counts = {}
                copilot_related = 0
                
                for alert in alerts_data.value:
                    # Count by severity
                    severity = getattr(alert, 'severity', 'Unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    # Count by category
                    category = getattr(alert, 'category', 'Unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
                    
                    # Check if Copilot-related (title/description contains copilot/AI keywords)
                    title = getattr(alert, 'title', '').lower()
                    description = getattr(alert, 'description', '').lower()
                    if any(keyword in title or keyword in description 
                           for keyword in ['copilot', 'ai', 'chatgpt', 'openai', 'agent', 'plugin']):
                        copilot_related += 1
                
                client.alert_summary['by_severity'] = severity_counts
                client.alert_summary['by_category'] = category_counts
                client.alert_summary['copilot_related'] = copilot_related
        elif graph_results.get('alerts') is None:
            # Security API unavailable - likely not activated
            with _stdout_lock:
                print(f"[{get_timestamp()}] ℹ️  Graph Security alerts unavailable - using license-based recommendations only")
        
        # Process Graph Security Incidents
        if graph_results.get('incidents'):
            incidents_data = graph_results['incidents']
            if hasattr(incidents_data, 'value') and incidents_data.value:
                client.security_incidents = incidents_data.value
                
                active = 0
                resolved = 0
                high_severity = 0
                
                for incident in incidents_data.value:
                    status = getattr(incident, 'status', '').lower()
                    if status in ['active', 'new', 'inprogress']:
                        active += 1
                    elif status in ['resolved', 'closed']:
                        resolved += 1
                    
                    severity = getattr(incident, 'severity', '').lower()
                    if severity == 'high':
                        high_severity += 1
                
                client.incident_summary = {
                    'total': len(incidents_data.value),
                    'active': active,
                    'resolved': resolved,
                    'high_severity': high_severity
                }
        
        # Process Secure Score
        if graph_results.get('secure_scores'):
            scores_data = graph_results['secure_scores']
            if hasattr(scores_data, 'value') and scores_data.value:
                # Get the latest score (first item)
                latest_score = scores_data.value[0]
                client.secure_score = latest_score
                
                current = getattr(latest_score, 'current_score', 0)
                max_score = getattr(latest_score, 'max_score', 0)
                percentage = (current / max_score * 100) if max_score > 0 else 0
                
                client.secure_score_summary = {
                    'current_score': current,
                    'max_score': max_score,
                    'percentage': round(percentage, 2)
                }
        
        # Process Secure Score Controls
        if graph_results.get('secure_score_controls'):
            controls_data = graph_results['secure_score_controls']
            if hasattr(controls_data, 'value') and controls_data.value:
                client.secure_score_controls = controls_data.value
                
                implemented = 0
                not_implemented = 0
                identity_controls = []
                data_controls = []
                copilot_relevant = 0
                
                for control in controls_data.value:
                    implementation_status = getattr(control, 'implementation_status', '').lower()
                    if implementation_status == 'implemented':
                        implemented += 1
                    else:
                        not_implemented += 1
                    
                    # Categorize controls by Copilot relevance
                    control_category = getattr(control, 'control_category', '').lower()
                    control_name = getattr(control, 'title', '').lower()
                    
                    if any(keyword in control_category or keyword in control_name for keyword in ['identity', 'authentication', 'mfa', 'conditional']):
                        identity_controls.append(control)
                    
                    if any(keyword in control_category or keyword in control_name for keyword in ['data', 'dlp', 'encryption', 'information']):
                        data_controls.append(control)
                    
                    if any(keyword in control_name for keyword in ['copilot', 'ai', 'agent', 'm365', 'office365', 'sharepoint', 'teams']):
                        copilot_relevant += 1
                
                client.identity_controls = identity_controls
                client.data_controls = data_controls
                
                client.control_summary = {
                    'total': len(controls_data.value),
                    'implemented': implemented,
                    'not_implemented': not_implemented
                }
                
                client.control_focus_summary = {
                    'identity_controls': len(identity_controls),
                    'data_controls': len(data_controls),
                    'copilot_relevant': copilot_relevant
                }
        
        # Process Risky Users (Identity Protection)
        if graph_results.get('risky_users'):
            risky_users_data = graph_results['risky_users']
            if hasattr(risky_users_data, 'value') and risky_users_data.value:
                client.risky_users = risky_users_data.value
                
                high = 0
                medium = 0
                low = 0
                confirmed_compromised = 0
                
                for user in risky_users_data.value:
                    risk_level = getattr(user, 'risk_level', '').lower()
                    risk_state = getattr(user, 'risk_state', '').lower()
                    
                    if risk_level == 'high':
                        high += 1
                    elif risk_level == 'medium':
                        medium += 1
                    elif risk_level == 'low':
                        low += 1
                    
                    if risk_state == 'confirmedcompromised':
                        confirmed_compromised += 1
                
                client.risky_users_summary = {
                    'total': len(risky_users_data.value),
                    'high': high,
                    'medium': medium,
                    'low': low,
                    'confirmed_compromised': confirmed_compromised
                }
        
        # Process Risky Sign-ins
        if graph_results.get('risky_sign_ins'):
            risky_sign_ins_data = graph_results['risky_sign_ins']
            if hasattr(risky_sign_ins_data, 'value') and risky_sign_ins_data.value:
                client.risky_sign_ins = risky_sign_ins_data.value
                
                high_risk = 0
                medium_risk = 0
                
                for sign_in in risky_sign_ins_data.value:
                    risk_level = getattr(sign_in, 'risk_level_aggregated', '').lower()
                    
                    if risk_level == 'high':
                        high_risk += 1
                    elif risk_level == 'medium':
                        medium_risk += 1
                
                client.risky_sign_ins_summary = {
                    'total': len(risky_sign_ins_data.value),
                    'high_risk': high_risk,
                    'medium_risk': medium_risk
                }
        
        # Process OAuth Permission Grants (third-party apps)
        if graph_results.get('oauth_grants'):
            oauth_grants_data = graph_results['oauth_grants']
            if hasattr(oauth_grants_data, 'value') and oauth_grants_data.value:
                # Group by client/app
                apps_by_client = {}
                for grant in oauth_grants_data.value:
                    client_id = getattr(grant, 'client_id', 'unknown')
                    if client_id not in apps_by_client:
                        apps_by_client[client_id] = []
                    apps_by_client[client_id].append(grant)
                
                client.oauth_apps = list(apps_by_client.values())
                
                # Analyze risk based on scope breadth
                high_risk = 0
                medium_risk = 0
                over_privileged = 0
                
                for app_grants in apps_by_client.values():
                    scopes = set()
                    for grant in app_grants:
                        scope_str = getattr(grant, 'scope', '')
                        if scope_str:
                            scopes.update(scope_str.split())
                    
                    # High-risk if has sensitive scopes
                    if any(s in scopes for s in ['Mail.ReadWrite', 'Files.ReadWrite.All', 'Sites.ReadWrite.All', 'User.ReadWrite.All']):
                        high_risk += 1
                    elif any(s in scopes for s in ['Mail.Read', 'Files.Read.All', 'Sites.Read.All']):
                        medium_risk += 1
                    
                    # Over-privileged if more than 10 scopes
                    if len(scopes) > 10:
                        over_privileged += 1
                
                client.oauth_risk_summary = {
                    'total_apps': len(apps_by_client),
                    'high_risk': high_risk,
                    'medium_risk': medium_risk,
                    'over_privileged': over_privileged
                }
        
    except Exception as e:
        with _stdout_lock:
            print(f"[{get_timestamp()}] ⚠️  Graph Security API failed: {str(e)[:150]}")
    
    # ========== PART 2: Microsoft 365 Defender API (direct API) ==========
    # More detailed data, but requires higher SKUs (E5, Defender plans)
    
    # DISABLED: Progress display causes deadlock
    # Will show results at the end instead
    
    try:
        # Get Graph/Security credential (Service Principal)
        from .get_graph_client import get_shared_credential
        credential = get_shared_credential()
        
        # Time filtering for Defender API
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
        
        defender_scope = "https://api.securitycenter.microsoft.com/.default"
        defender_token = credential.get_token(defender_scope)
        
        # Decode token to verify permissions
        import base64
        import json
        token_parts = defender_token.token.split('.')
        # Add padding if needed
        payload = token_parts[1] + '=' * (4 - len(token_parts[1]) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload))
        roles = decoded.get('roles', [])
        
        # Create HTTP client for Defender API
        import httpx
        defender_http = httpx.AsyncClient(
            base_url="https://api.security.microsoft.com",
            headers={
                "Authorization": f"Bearer {defender_token.token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        defender_tasks = {}
        
        # Fetch incidents (more detailed than Graph version)
        defender_tasks['incidents'] = defender_http.get("/api/incidents")
        
        # Fetch machines/devices (Defender for Endpoint)
        defender_tasks['machines'] = defender_http.get("/api/machines")
        
        # Fetch vulnerabilities (Defender for Endpoint)
        defender_tasks['vulnerabilities'] = defender_http.get("/api/vulnerabilities")
        
        # Advanced Hunting: Copilot-related security events (multiple queries)
        # Query 1: Copilot process activity (potential malicious automation)
        copilot_process_query = """
        DeviceProcessEvents
        | where Timestamp > ago(30d)
        | where ProcessCommandLine has_any ('copilot', 'bing chat', 'edge://copilot', 'teams copilot')
            or InitiatingProcessCommandLine has_any ('copilot', 'ai assistant')
        | where ActionType in ('ProcessCreated', 'ScriptExecution')
        | summarize 
            TotalEvents=count(),
            UniqueSuspiciousProcesses=dcount(FileName),
            UniqueDevices=dcount(DeviceName),
            SuspiciousCommandLines=make_set(ProcessCommandLine, 10)
            by DeviceName, AccountName
        | where TotalEvents > 5  // Filter noise
        | order by TotalEvents desc
        | limit 100
        """
        
        # Query 2: Copilot-related network activity (data exfiltration risk)
        copilot_network_query = """
        DeviceNetworkEvents
        | where Timestamp > ago(30d)
        | where RemoteUrl has_any ('openai.com', 'copilot', 'bing.com/chat', 'ai.azure.com')
            or InitiatingProcessFileName has_any ('Teams.exe', 'msedge.exe', 'powerpnt.exe', 'winword.exe', 'excel.exe')
        | where ActionType in ('ConnectionSuccess', 'ConnectionRequest')
        | summarize 
            TotalConnections=count(),
            UniqueURLs=dcount(RemoteUrl),
            DataSent=sum(tolong(RemoteSentBytes)),
            DataReceived=sum(tolong(RemoteReceivedBytes)),
            RemoteURLs=make_set(RemoteUrl, 10)
            by DeviceName, InitiatingProcessFileName
        | extend DataSentMB = DataSent / 1024 / 1024
        | extend DataReceivedMB = DataReceived / 1024 / 1024
        | where DataSentMB > 10 or TotalConnections > 100  // Unusual volume
        | order by DataSentMB desc
        | limit 100
        """
        
        # Query 3: File access patterns (sensitive documents accessed before Copilot use)
        copilot_file_access_query = """
        DeviceFileEvents
        | where Timestamp > ago(30d)
        | where InitiatingProcessFileName has_any ('Teams.exe', 'msedge.exe', 'OneDrive.exe')
        | where SensitivityLabel in ('Highly Confidential', 'Confidential', 'Secret')
            or FileName endswith_any ('.docx', '.xlsx', '.pptx', '.pdf')
        | where ActionType in ('FileCreated', 'FileModified', 'FileRenamed', 'FileCopied')
        | summarize 
            TotalFileOperations=count(),
            UniqueSensitiveFiles=dcount(FileName),
            FileTypes=make_set(FileExtension, 10)
            by DeviceName, AccountName, InitiatingProcessFileName
        | where TotalFileOperations > 20  // Significant activity
        | order by UniqueSensitiveFiles desc
        | limit 100
        """
        
        # Query 4: Email threats mentioning Copilot/AI (social engineering)
        copilot_email_query = """
        EmailEvents
        | where Timestamp > ago(30d)
        | where Subject has_any ('copilot', 'AI assistant', 'chatgpt', 'openai', 'artificial intelligence')
            or EmailDirection == 'Inbound'
        | where ThreatTypes has_any ('Phish', 'Malware', 'Spam')
        | summarize 
            TotalThreats=count(),
            PhishingAttempts=countif(ThreatTypes has 'Phish'),
            MalwareAttempts=countif(ThreatTypes has 'Malware'),
            UniqueSenders=dcount(SenderFromAddress),
            Senders=make_set(SenderFromAddress, 10)
            by RecipientEmailAddress
        | order by TotalThreats desc
        | limit 100
        """
        
        # Execute all Advanced Hunting queries
        defender_tasks['hunting_copilot_processes'] = defender_http.post(
            "/api/advancedhunting/run",
            json={"Query": copilot_process_query}
        )
        
        defender_tasks['hunting_copilot_network'] = defender_http.post(
            "/api/advancedhunting/run",
            json={"Query": copilot_network_query}
        )
        
        defender_tasks['hunting_copilot_files'] = defender_http.post(
            "/api/advancedhunting/run",
            json={"Query": copilot_file_access_query}
        )
        
        defender_tasks['hunting_copilot_emails'] = defender_http.post(
            "/api/advancedhunting/run",
            json={"Query": copilot_email_query}
        )
        
        # Fetch email threats (post-delivery detections for phishing/malware in Copilot content)
        # Filter for last 30 days
        defender_tasks['email_threats'] = defender_http.get(
            f"/api/EmailPostDeliveryDetections?$filter=DetectionTime ge {thirty_days_ago}"
        )
        
        # Fetch security recommendations (missing controls, configuration gaps)
        defender_tasks['recommendations'] = defender_http.get("/api/recommendations")
        
        # Fetch software inventory (for Copilot app detection)
        defender_tasks['software'] = defender_http.get("/api/Software")
        
        # Fetch exposure score (overall security posture)
        defender_tasks['exposure_score'] = defender_http.get("/api/exposureScore")
        
        # Execute all Defender API calls in parallel using gather (like Graph Security)
        results = await asyncio.gather(*defender_tasks.values(), return_exceptions=True)
        
        # Process results and match them to task names
        defender_results = {}
        for (key, task), response in zip(defender_tasks.items(), results):
            if isinstance(response, Exception):
                error_msg = str(response)
                if 'not provisioned' in error_msg.lower():
                    client.activation_needed = True
                    if not client.activation_message:
                        client.activation_message = "Microsoft Defender for Endpoint not activated"
                else:
                    with _stdout_lock:
                        print(f"[{get_timestamp()}] ⚠️  Defender API ({key}): {str(response)[:100]}")
                defender_results[key] = None
            elif hasattr(response, 'status_code'):
                if response.status_code == 200:
                    json_data = response.json()
                    defender_results[key] = json_data
                    client.defender_api_available = True
                    
                    # Count items returned
                    item_count = 0
                    if isinstance(json_data, dict):
                        if 'value' in json_data:
                            item_count = len(json_data['value'])
                        elif 'Results' in json_data:
                            item_count = len(json_data['Results'])
                        elif key == 'exposure_score':
                            item_count = 1 if json_data.get('score') is not None else 0
                    
                    print(f"[{get_timestamp()}] ✓ Defender API ({key}): Success - {item_count} items returned")
                elif response.status_code == 403:
                    # 403 Forbidden - track silently (recommendation will report this)
                    client.activation_needed = True
                    if not client.activation_message:
                        client.activation_message = "Microsoft Defender for Endpoint API access denied - likely no devices onboarded"
                    defender_results[key] = None
                elif response.status_code == 404:
                    # 404 Not Found - track silently (recommendation will report this)
                    client.missing_features.append(key)
                    defender_results[key] = None
                else:
                    defender_results[key] = None
            else:
                defender_results[key] = None
        
        # Progress display disabled
        successful_defender = sum(1 for v in defender_results.values() if v is not None and not isinstance(v, Exception))
        
        # Show single summary message
        if successful_defender == 0:
            print(f"[{get_timestamp()}] ⚠️  Defender API: 0/{len(defender_tasks)} datasets fetched (permissions not granted or no devices onboarded)")
        else:
            print(f"[{get_timestamp()}] ✓ Defender API: {successful_defender}/{len(defender_tasks)} datasets fetched")
        
        # Process Defender Incidents
        if defender_results.get('incidents') and isinstance(defender_results['incidents'], dict):
            incidents = defender_results['incidents'].get('value', [])
            client.defender_incidents = incidents
            
            in_progress = sum(1 for i in incidents if i.get('status', '').lower() in ['active', 'inprogress'])
            new = sum(1 for i in incidents if i.get('status', '').lower() == 'new')
            
            client.defender_incident_summary = {
                'total': len(incidents),
                'in_progress': in_progress,
                'new': new
            }
        
        # Process Defender Devices/Machines
        if defender_results.get('machines') and isinstance(defender_results['machines'], dict):
            machines = defender_results['machines'].get('value', [])
            client.defender_devices = machines
            
            high_risk = 0
            medium_risk = 0
            low_risk = 0
            copilot_enabled = 0
            
            for machine in machines:
                risk_score = machine.get('riskScore', 'None')
                if risk_score == 'High':
                    high_risk += 1
                elif risk_score == 'Medium':
                    medium_risk += 1
                elif risk_score == 'Low':
                    low_risk += 1
                
                # Check if device has Teams/M365 apps (proxy for Copilot enablement)
                software = machine.get('softwareInventory', [])
                if any('teams' in str(s).lower() or 'microsoft 365' in str(s).lower() for s in software):
                    copilot_enabled += 1
            
            client.device_summary = {
                'total': len(machines),
                'high_risk': high_risk,
                'medium_risk': medium_risk,
                'low_risk': low_risk,
                'copilot_enabled': copilot_enabled
            }
        
        # Process Vulnerabilities
        if defender_results.get('vulnerabilities') and isinstance(defender_results['vulnerabilities'], dict):
            vulns = defender_results['vulnerabilities'].get('value', [])
            client.defender_vulnerabilities = vulns
            
            critical = sum(1 for v in vulns if v.get('severity', '').lower() == 'critical')
            high = sum(1 for v in vulns if v.get('severity', '').lower() == 'high')
            medium = sum(1 for v in vulns if v.get('severity', '').lower() == 'medium')
            low = sum(1 for v in vulns if v.get('severity', '').lower() == 'low')
            
            client.vulnerability_summary = {
                'total': len(vulns),
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low
            }
        
        # Process Advanced Hunting Results - Copilot Process Events
        if defender_results.get('hunting_copilot_processes') and isinstance(defender_results['hunting_copilot_processes'], dict):
            results = defender_results['hunting_copilot_processes'].get('Results', [])
            client.copilot_process_events = {'results': results, 'count': len(results)}
            
            if results:
                client.hunting_summary['suspicious_processes'] = sum(r.get('TotalEvents', 0) for r in results)
                client.hunting_summary['affected_devices'] += len(set(r.get('DeviceName', '') for r in results if r.get('DeviceName')))
                client.hunting_summary['affected_users'] += len(set(r.get('AccountName', '') for r in results if r.get('AccountName')))
        
        # Process Advanced Hunting Results - Copilot Network Events
        if defender_results.get('hunting_copilot_network') and isinstance(defender_results['hunting_copilot_network'], dict):
            results = defender_results['hunting_copilot_network'].get('Results', [])
            client.copilot_network_events = {'results': results, 'count': len(results)}
            
            if results:
                client.hunting_summary['unusual_network_activity'] = sum(r.get('TotalConnections', 0) for r in results)
                client.hunting_summary['affected_devices'] += len(set(r.get('DeviceName', '') for r in results if r.get('DeviceName')))
        
        # Process Advanced Hunting Results - Copilot File Access
        if defender_results.get('hunting_copilot_files') and isinstance(defender_results['hunting_copilot_files'], dict):
            results = defender_results['hunting_copilot_files'].get('Results', [])
            client.copilot_file_access_events = {'results': results, 'count': len(results)}
            
            if results:
                client.hunting_summary['sensitive_file_access'] = sum(r.get('UniqueSensitiveFiles', 0) for r in results)
                client.hunting_summary['affected_devices'] += len(set(r.get('DeviceName', '') for r in results if r.get('DeviceName')))
                client.hunting_summary['affected_users'] += len(set(r.get('AccountName', '') for r in results if r.get('AccountName')))
        
        # Process Advanced Hunting Results - Copilot Email Threats
        if defender_results.get('hunting_copilot_emails') and isinstance(defender_results['hunting_copilot_emails'], dict):
            results = defender_results['hunting_copilot_emails'].get('Results', [])
            client.copilot_email_threats = {'results': results, 'count': len(results)}
            
            if results:
                client.hunting_summary['phishing_attempts'] = sum(r.get('PhishingAttempts', 0) for r in results)
        
        # Deduplicate device/user counts (same device/user may appear in multiple queries)
        # Note: This is approximate, actual deduplication would require cross-query correlation
        
        # Process Email Threats (post-delivery detections)
        if defender_results.get('email_threats') and isinstance(defender_results['email_threats'], dict):
            email_threats = defender_results['email_threats'].get('value', [])
            client.email_threats = email_threats
            
            phishing = sum(1 for e in email_threats if 'phish' in str(e.get('threatType', '')).lower())
            malware = sum(1 for e in email_threats if 'malware' in str(e.get('threatType', '')).lower())
            spam = sum(1 for e in email_threats if 'spam' in str(e.get('threatType', '')).lower())
            
            client.email_threat_summary = {
                'total': len(email_threats),
                'phishing': phishing,
                'malware': malware,
                'spam': spam
            }
        
        # Process Security Recommendations (configuration gaps)
        if defender_results.get('recommendations') and isinstance(defender_results['recommendations'], dict):
            recommendations = defender_results['recommendations'].get('value', [])
            client.security_recommendations = recommendations
            
            critical = sum(1 for r in recommendations if r.get('severity', '').lower() == 'critical')
            high = sum(1 for r in recommendations if r.get('severity', '').lower() == 'high')
            
            # Check for Copilot-related recommendations
            copilot_related = 0
            for rec in recommendations:
                rec_name = str(rec.get('recommendationName', '')).lower()
                rec_category = str(rec.get('recommendationCategory', '')).lower()
                if any(keyword in rec_name or keyword in rec_category for keyword in 
                       ['microsoft 365', 'm365', 'office', 'teams', 'sharepoint', 'onedrive', 'exchange', 'identity', 'authentication', 'mfa']):
                    copilot_related += 1
            
            client.recommendations_summary = {
                'total': len(recommendations),
                'critical': critical,
                'high': high,
                'copilot_related': copilot_related
            }
        
        # Process Software Inventory (Copilot app detection)
        if defender_results.get('software') and isinstance(defender_results['software'], dict):
            software = defender_results['software'].get('value', [])
            client.software_inventory = software
            
            # Detect Copilot-related apps
            copilot_apps = 0
            vulnerable_apps = 0
            
            for app in software:
                app_name = str(app.get('name', '')).lower()
                vendor = str(app.get('vendor', '')).lower()
                
                # Count Copilot-related apps
                if any(keyword in app_name or keyword in vendor for keyword in 
                       ['microsoft teams', 'microsoft 365', 'edge', 'copilot', 'office']):
                    copilot_apps += 1
                
                # Count vulnerable apps
                if app.get('numberOfWeaknesses', 0) > 0:
                    vulnerable_apps += 1
            
            client.software_summary = {
                'total_apps': len(software),
                'copilot_apps': copilot_apps,
                'vulnerable_apps': vulnerable_apps
            }
        
        # Process Exposure Score (overall security posture)
        if defender_results.get('exposure_score') and isinstance(defender_results['exposure_score'], dict):
            client.exposure_score = defender_results['exposure_score']
            
            score = defender_results['exposure_score'].get('score', 0)
            # Exposure score: Lower is better (0-100, where 0 is best)
            if score <= 30:
                level = 'Low Risk'
            elif score <= 60:
                level = 'Medium Risk'
            else:
                level = 'High Risk'
            
            client.exposure_summary = {
                'score': score,
                'level': level,
                'trend': defender_results['exposure_score'].get('rbacGroupName', 'Unknown')  # Trend not always available
            }
        
        # Close Defender HTTP client
        await defender_http.aclose()
        
        # Mark overall availability
        client.available = client.graph_security_available or client.defender_api_available
        
        with _stdout_lock:
            print(f"[{get_timestamp()}] ✅ Defender client initialized (Graph Security: {client.graph_security_available}, Defender API: {client.defender_api_available})")
    
    except Exception as e:
        with _stdout_lock:
            print(f"[{get_timestamp()}] ⚠️  Defender API section failed: {str(e)[:150]}")
    
    return client


async def _load_delegated_defender_data(json_data, graph_client):
    """Load Defender data collected via delegated authentication (PowerShell wrapper)"""
    
    # Create client instance
    class DefenderClient:
        def __init__(self):
            self.available = True
            self.graph_security_available = True  # Still fetch from Graph Security
            self.defender_api_available = True  # Data from delegated auth
            self.activation_needed = False
            self.missing_features = []
            
            # Initialize all data structures (same as main client)
            self.security_alerts = []
            self.alert_summary = {'total': 0, 'by_severity': {}, 'by_category': {}, 'copilot_related': 0}
            self.security_incidents = []
            self.incident_summary = {'total': 0, 'active': 0, 'resolved': 0, 'high_severity': 0}
            self.secure_score = {}
            self.secure_score_summary = {'current_score': 0, 'max_score': 0, 'percentage': 0}
            self.secure_score_controls = []
            self.control_summary = {'total': 0, 'implemented': 0, 'not_implemented': 0}
            self.defender_incidents = []
            self.defender_incident_summary = {'total': 0, 'in_progress': 0, 'new': 0}
            self.defender_devices = []
            self.device_summary = {'total': 0, 'high_risk': 0, 'medium_risk': 0, 'low_risk': 0, 'copilot_enabled': 0}
            self.defender_vulnerabilities = []
            self.vulnerability_summary = {'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            self.risky_users = []
            self.risky_users_summary = {'total': 0, 'high': 0, 'medium': 0, 'low': 0, 'confirmed_compromised': 0}
            self.email_threats = []
            self.email_threat_summary = {'total': 0, 'phishing': 0, 'malware': 0, 'spam': 0}
            self.oauth_apps = []
            self.oauth_risk_summary = {'total_apps': 0, 'high_risk': 0, 'medium_risk': 0, 'over_privileged': 0}
            self.exposure_summary = {'score': 0, 'level': 'Unknown', 'trend': 'Unknown'}
    
    client = DefenderClient()
    
    # Parse JSON data from PowerShell
    try:
        data = json.loads(json_data)
        
        # Map delegated data to client properties
        if data.get('incidents'):
            client.defender_incidents = data['incidents'].get('value', [])
            client.defender_incident_summary['total'] = len(client.defender_incidents)
        
        if data.get('machines'):
            client.defender_devices = data['machines'].get('value', [])
            client.device_summary['total'] = len(client.defender_devices)
        
        if data.get('vulnerabilities'):
            client.defender_vulnerabilities = data['vulnerabilities'].get('value', [])
            client.vulnerability_summary['total'] = len(client.defender_vulnerabilities)
        
        if data.get('recommendations'):
            # Store recommendations data
            client.security_recommendations = data['recommendations'].get('value', [])
        
        if data.get('software'):
            client.software_inventory = data['software'].get('value', [])
        
        if data.get('exposure_score'):
            score = data['exposure_score'].get('score', 0)
            client.exposure_summary['score'] = score
            if score >= 80:
                client.exposure_summary['level'] = 'Low Risk'
            elif score >= 60:
                client.exposure_summary['level'] = 'Medium Risk'
            else:
                client.exposure_summary['level'] = 'High Risk'
        
        with _stdout_lock:
            print(f"[{get_timestamp()}] ✓ Loaded Defender data: {client.device_summary['total']} devices, {client.defender_incident_summary['total']} incidents")
    
    except Exception as e:
        with _stdout_lock:
            print(f"[{get_timestamp()}] ⚠️  Error parsing delegated Defender data: {str(e)}")
    
    # Still fetch Graph Security data using service principal
    try:
        # Fetch Graph Security API data (same as before)
        from msgraph.generated.security.alerts_v2.alerts_v2_request_builder import AlertsV2RequestBuilder
        
        alerts = await graph_client.security.alerts_v2.get()
        if alerts and alerts.value:
            client.security_alerts = alerts.value
            client.alert_summary['total'] = len(alerts.value)
        
        with _stdout_lock:
            print(f"[{get_timestamp()}] ✓ Graph Security: {client.alert_summary['total']} alerts")
    
    except Exception as e:
        with _stdout_lock:
            print(f"[{get_timestamp()}] ⚠️  Graph Security API failed: {str(e)[:100]}")
    
    return client
