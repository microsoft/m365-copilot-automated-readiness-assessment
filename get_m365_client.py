"""
Microsoft 365 Usage & Deployment Client
Provides authenticated access to Microsoft Graph usage reports and deployment data.
Fetches and caches: usage reports, site metadata, user assignments, activity metrics.
Used for enhanced M365 Copilot adoption observations.
"""
import asyncio
import csv
import io
from azure.core.exceptions import HttpResponseError
from spinner import get_timestamp, _stdout_lock
from datetime import datetime, timedelta

async def get_m365_client(graph_client):
    """
    Get M365 usage analytics and deployment data from Microsoft Graph.
    Fetches comprehensive usage reports and metadata for Copilot readiness assessment.
    
    Args:
        graph_client: Existing Microsoft Graph SDK client
    
    Returns:
        Object with cached M365 data from Graph API,
        or minimal client if permissions are insufficient (graceful degradation)
    """
    
    # Helper function to parse CSV reports from Graph API
    def parse_csv_report(report_data):
        """Parse binary CSV data from Graph API reports into list of dicts"""
        if not report_data:
            return []
        
        try:
            # Graph API returns bytes, decode to string
            if isinstance(report_data, bytes):
                csv_text = report_data.decode('utf-8-sig')  # BOM-aware
            else:
                csv_text = str(report_data)
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(csv_text))
            return list(reader)
        except Exception:
            return []
    
    # Create a simple object to store fetched data
    class M365Client:
        def __init__(self):
            self.available = False
            
            # Raw data storage
            self.sites = []
            self.users = []
            
            # Pre-computed summaries for fast access
            self.sites_summary = {}
            self.users_summary = {}
            self.email_summary = {}
            self.teams_summary = {}
            self.sharepoint_summary = {}
            self.onedrive_summary = {}
            self.activations_summary = {}
            self.active_users_summary = {}
            
            # Track missing features/permissions
            self.missing_permissions = []
    
    client = M365Client()
    
    try:
        # Phase 1: Fetch core data in parallel
        # These are the most critical for M365 Copilot observations
        
        # Build tasks for parallel execution
        # Errors are handled by asyncio.gather(return_exceptions=True)
        report_period = 'D30'
        
        # Build request configuration for users query
        from msgraph.generated.users.users_request_builder import UsersRequestBuilder
        users_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                top=999,
                select=['id', 'displayName', 'userPrincipalName', 'assignedLicenses', 'accountEnabled']
            )
        )
        
        # Create tasks with labels for progress tracking
        tasks = {
            'sites': graph_client.sites.get(),
            'users': graph_client.users.get(request_configuration=users_config),
            'email_activity': graph_client.reports.get_email_activity_user_detail_with_period(period=report_period).get(),
            'teams_activity': graph_client.reports.get_teams_user_activity_user_detail_with_period(period=report_period).get(),
            'sharepoint_usage': graph_client.reports.get_share_point_site_usage_detail_with_period(period=report_period).get(),
            'onedrive_usage': graph_client.reports.get_one_drive_usage_account_detail_with_period(period=report_period).get(),
            'office_activations': graph_client.reports.get_office365_activations_user_detail.get(),
            'active_users': graph_client.reports.get_office365_active_user_detail_with_period(period=report_period).get()
        }
        
        # Execute all API calls in parallel with progress bar
        import sys
        from spinner import _stdout_lock, get_timestamp
        
        # Show initial progress bar
        with _stdout_lock:
            sys.stdout.write(f'\r[{get_timestamp()}]   M365 Data Gathering     [░░░░░░░░░░░░░░░░░░░░]   0%')
            sys.stdout.flush()
        
        # Create progress update task
        async def update_progress():
            for i in range(1, 101):
                await asyncio.sleep(0.6)  # ~60 seconds total
                progress = i / 100
                filled = int(20 * progress)
                bar = '█' * filled + '░' * (20 - filled)
                with _stdout_lock:
                    sys.stdout.write(f'\r[{get_timestamp()}]   M365 Data Gathering     [{bar}] {i:3d}%')
                    sys.stdout.flush()
        
        # Run API calls and progress updates concurrently
        progress_task = asyncio.create_task(update_progress())
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        progress_task.cancel()
        
        # Complete progress bar
        with _stdout_lock:
            sys.stdout.write(f'\r[{get_timestamp()}]   ✓ M365 Data Gathering     [████████████████████] 100%\n')
            sys.stdout.flush()
        
        # Map results to named dictionary
        response_dict = dict(zip(tasks.keys(), results))
        
        # Process Sites data
        sites_response = response_dict.get('sites')
        if not isinstance(sites_response, Exception) and sites_response:
            try:
                client.sites = sites_response.value if hasattr(sites_response, 'value') else []
                client.available = True
                
                # Pre-compute sites summary
                total_sites = len(client.sites)
                client.sites_summary = {
                    'total': total_sites,
                    'site_names': [site.display_name for site in client.sites if hasattr(site, 'display_name')],
                    'root_site_id': client.sites[0].id if total_sites > 0 and hasattr(client.sites[0], 'id') else None
                }
            except Exception as e:
                client.sites_summary = {'total': 0, 'error': f'Failed to process sites: {str(e)}'}
        else:
            client.sites_summary = {'total': 0, 'error': 'Sites.Read.All permission missing or API error'}
            client.missing_permissions.append('Sites.Read.All')
        
        # Process Users data
        users_response = response_dict.get('users')
        if not isinstance(users_response, Exception) and users_response:
            try:
                client.users = users_response.value if hasattr(users_response, 'value') else []
                client.available = True
                
                # Analyze user license assignments
                total_users = len(client.users)
                enabled_users = sum(1 for u in client.users if getattr(u, 'account_enabled', True))
                
                # Count Copilot license assignments (SKU IDs for M365 Copilot)
                copilot_sku_ids = [
                    'c28afa23-5a37-4837-938f-7cc48d0cca5c',  # M365 Copilot
                    'f2b5e97e-f677-4bb5-8127-5c3ce7b6a64e',  # M365 Copilot (User)
                ]
                copilot_sku_ids_lower = [sku.lower() for sku in copilot_sku_ids]  # Compute once
                
                copilot_licensed = 0
                for user in client.users:
                    if hasattr(user, 'assigned_licenses') and user.assigned_licenses:
                        for license in user.assigned_licenses:
                            if hasattr(license, 'sku_id') and str(license.sku_id).lower() in copilot_sku_ids_lower:
                                copilot_licensed += 1
                                break
                
                client.users_summary = {
                    'total': total_users,
                    'enabled': enabled_users,
                    'disabled': total_users - enabled_users,
                    'copilot_licensed': copilot_licensed,
                    'copilot_adoption_rate': round((copilot_licensed / total_users * 100), 2) if total_users > 0 else 0,
                    'sampled': total_users >= 999  # Flag if we hit the limit
                }
            except Exception as e:
                client.users_summary = {'total': 0, 'error': f'Failed to process users: {str(e)}'}
        else:
            client.users_summary = {'total': 0, 'error': 'User.Read.All permission missing or API error'}
            client.missing_permissions.append('User.Read.All')
        
        # Process Email Activity Report
        # Parse CSV and extract key metrics for Exchange/Outlook observations
        email_response = response_dict.get('email_activity')
        if not isinstance(email_response, Exception) and email_response:
            parsed_rows = parse_csv_report(email_response)
            
            if parsed_rows:
                client.available = True
                # Aggregate metrics in single pass over CSV rows
                send_count = 0
                receive_count = 0
                read_count = 0
                
                for row in parsed_rows:
                    send_count += int(row.get('Send Count', 0) or 0)
                    receive_count += int(row.get('Receive Count', 0) or 0)
                    read_count += int(row.get('Read Count', 0) or 0)
                
                total_users_with_activity = len(parsed_rows)
                
                client.email_summary = {
                    'available': True,
                    'report_period': report_period,
                    'active_users': total_users_with_activity,
                    'total_sent': send_count,
                    'total_received': receive_count,
                    'total_read': read_count,
                    'avg_sent_per_user': round(send_count / total_users_with_activity, 1) if total_users_with_activity > 0 else 0,
                    'avg_received_per_user': round(receive_count / total_users_with_activity, 1) if total_users_with_activity > 0 else 0
                }
            else:
                client.email_summary = {'available': False, 'error': 'No data in report'}
        else:
            client.email_summary = {'available': False}
            if 'Reports.Read.All' not in client.missing_permissions:
                client.missing_permissions.append('Reports.Read.All')
        
        # Process Teams Activity Report
        # Parse CSV and extract Teams usage metrics
        teams_response = response_dict.get('teams_activity')
        if not isinstance(teams_response, Exception) and teams_response:
            parsed_rows = parse_csv_report(teams_response)
            
            if parsed_rows:
                client.available = True
                # Aggregate Teams metrics in single pass
                chat_messages = 0
                private_messages = 0
                calls = 0
                meetings = 0
                
                for row in parsed_rows:
                    chat_messages += int(row.get('Team Chat Message Count', 0) or 0)
                    private_messages += int(row.get('Private Chat Message Count', 0) or 0)
                    calls += int(row.get('Call Count', 0) or 0)
                    meetings += int(row.get('Meeting Count', 0) or 0)
                
                total_users_with_activity = len(parsed_rows)
                
                client.teams_summary = {
                    'available': True,
                    'report_period': report_period,
                    'active_users': total_users_with_activity,
                    'total_team_chat_messages': chat_messages,
                    'total_private_messages': private_messages,
                    'total_calls': calls,
                    'total_meetings': meetings,
                    'avg_meetings_per_user': round(meetings / total_users_with_activity, 1) if total_users_with_activity > 0 else 0,
                    'avg_messages_per_user': round((chat_messages + private_messages) / total_users_with_activity, 1) if total_users_with_activity > 0 else 0
                }
            else:
                client.teams_summary = {'available': False, 'error': 'No data in report'}
        else:
            client.teams_summary = {'available': False}
        
        # Process SharePoint Usage Report
        # Parse CSV and extract SharePoint site metrics
        sharepoint_response = response_dict.get('sharepoint_usage')
        if not isinstance(sharepoint_response, Exception) and sharepoint_response:
            parsed_rows = parse_csv_report(sharepoint_response)
            
            if parsed_rows:
                client.available = True
                # Aggregate SharePoint metrics in single pass
                total_files = 0
                total_page_views = 0
                active_sites = 0
                
                for row in parsed_rows:
                    total_files += int(row.get('File Count', 0) or 0)
                    page_views = int(row.get('Page View Count', 0) or 0)
                    total_page_views += page_views
                    if page_views > 0:
                        active_sites += 1
                
                total_sites_in_report = len(parsed_rows)
                
                client.sharepoint_summary = {
                    'available': True,
                    'report_period': report_period,
                    'sites_in_report': total_sites_in_report,
                    'active_sites': active_sites,
                    'total_files': total_files,
                    'total_page_views': total_page_views,
                    'avg_files_per_site': round(total_files / total_sites_in_report, 1) if total_sites_in_report > 0 else 0,
                    'site_activity_rate': round((active_sites / total_sites_in_report * 100), 1) if total_sites_in_report > 0 else 0
                }
            else:
                client.sharepoint_summary = {'available': False, 'error': 'No data in report'}
        else:
            client.sharepoint_summary = {'available': False}
        
        # Process OneDrive Usage Report
        # Parse CSV and extract OneDrive adoption metrics
        onedrive_response = response_dict.get('onedrive_usage')
        if not isinstance(onedrive_response, Exception) and onedrive_response:
            parsed_rows = parse_csv_report(onedrive_response)
            
            if parsed_rows:
                client.available = True
                # Aggregate OneDrive metrics in single pass
                active_accounts = 0
                total_files = 0
                storage_used_bytes = 0
                
                for row in parsed_rows:
                    if row.get('Is Active', 'False') == 'True' or int(row.get('File Count', 0) or 0) > 0:
                        active_accounts += 1
                    total_files += int(row.get('File Count', 0) or 0)
                    storage_used_bytes += int(row.get('Storage Used (Byte)', 0) or 0)
                
                total_accounts = len(parsed_rows)
                storage_used_gb = round(storage_used_bytes / (1024**3), 2)
                
                client.onedrive_summary = {
                    'available': True,
                    'report_period': report_period,
                    'total_accounts': total_accounts,
                    'active_accounts': active_accounts,
                    'adoption_rate': round((active_accounts / total_accounts * 100), 1) if total_accounts > 0 else 0,
                    'total_files': total_files,
                    'storage_used_gb': storage_used_gb,
                    'avg_files_per_user': round(total_files / active_accounts, 1) if active_accounts > 0 else 0
                }
            else:
                client.onedrive_summary = {'available': False, 'error': 'No data in report'}
        else:
            client.onedrive_summary = {'available': False}
        
        # Process Office Activations Report
        # Parse CSV and extract Office app activation metrics
        activations_response = response_dict.get('office_activations')
        if not isinstance(activations_response, Exception) and activations_response:
            parsed_rows = parse_csv_report(activations_response)
            
            if parsed_rows:
                client.available = True
                # Count activation types in single pass
                windows_activations = 0
                mac_activations = 0
                mobile_activations = 0
                
                for row in parsed_rows:
                    if int(row.get('Windows', 0) or 0) > 0:
                        windows_activations += 1
                    if int(row.get('Mac', 0) or 0) > 0:
                        mac_activations += 1
                    if int(row.get('Android', 0) or 0) > 0 or int(row.get('iOS', 0) or 0) > 0:
                        mobile_activations += 1
                
                total_users_with_activations = len(parsed_rows)
                
                client.activations_summary = {
                    'available': True,
                    'total_users_with_activations': total_users_with_activations,
                    'windows_users': windows_activations,
                    'mac_users': mac_activations,
                    'mobile_users': mobile_activations,
                    'desktop_adoption_rate': round(((windows_activations + mac_activations) / total_users_with_activations * 100), 1) if total_users_with_activations > 0 else 0
                }
            else:
                client.activations_summary = {'available': False, 'error': 'No data in report'}
        else:
            client.activations_summary = {'available': False}
        
        # Process Active Users Report
        # Parse CSV and extract cross-service activity metrics
        active_users_response = response_dict.get('active_users')
        if not isinstance(active_users_response, Exception) and active_users_response:
            parsed_rows = parse_csv_report(active_users_response)
            
            if parsed_rows:
                client.available = True
                # Extract latest row (most recent date) for current snapshot
                if parsed_rows:
                    latest_row = parsed_rows[-1]  # CSV is sorted by date, last row is most recent
                    
                    client.active_users_summary = {
                        'available': True,
                        'report_period': report_period,
                        'office_365_active': int(latest_row.get('Office 365', 0) or 0),
                        'exchange_active': int(latest_row.get('Exchange', 0) or 0),
                        'onedrive_active': int(latest_row.get('OneDrive', 0) or 0),
                        'sharepoint_active': int(latest_row.get('SharePoint', 0) or 0),
                        'teams_active': int(latest_row.get('Microsoft Teams', 0) or 0),
                        'yammer_active': int(latest_row.get('Yammer', 0) or 0)
                    }
                else:
                    client.active_users_summary = {'available': False, 'error': 'No rows in report'}
            else:
                client.active_users_summary = {'available': False, 'error': 'No data in report'}
        else:
            client.active_users_summary = {'available': False}
        
        # Log summary
        if client.available:
            successful_apis = sum([
                1 if client.sites_summary.get('total', 0) > 0 else 0,
                1 if client.users_summary.get('total', 0) > 0 else 0,
                1 if client.email_summary.get('available', False) else 0,
                1 if client.teams_summary.get('available', False) else 0,
                1 if client.sharepoint_summary.get('available', False) else 0,
                1 if client.onedrive_summary.get('available', False) else 0,
                1 if client.activations_summary.get('available', False) else 0,
                1 if client.active_users_summary.get('available', False) else 0
            ])
            
            # Success message removed for cleaner output
            if client.missing_permissions:
                with _stdout_lock:
                    print(f"[{get_timestamp()}] ⚠️  Missing permissions: {', '.join(client.missing_permissions)}")
        else:
            with _stdout_lock:
                print(f"[{get_timestamp()}] ⚠️  M365 client: No data available (check permissions)")
        
        return client
        
    except Exception as e:
        # Catastrophic error - return minimal client
        with _stdout_lock:
            print(f"[{get_timestamp()}] ⚠️  M365 client initialization failed: {str(e)}")
        
        client.available = False
        return client


def extract_m365_insights_from_client(m365_client):
    """
    Extract M365 usage insights from cached client data.
    Call this ONCE and reuse the result across all recommendations to avoid redundant processing.
    
    Args:
        m365_client: M365Client object with cached API data
    
    Returns:
        dict with pre-computed metrics for M365 Copilot adoption observations
    """
    if not m365_client or not m365_client.available:
        return {
            'available': False,
            
            # Sites & SharePoint
            'total_sites': 0,
            'sharepoint_active_sites': 0,
            'sharepoint_total_files': 0,
            'sharepoint_activity_rate': 0,
            
            # Users & Licensing
            'total_users': 0,
            'enabled_users': 0,
            'copilot_licensed_users': 0,
            'copilot_adoption_rate': 0,
            
            # Email Activity
            'email_active_users': 0,
            'email_avg_sent_per_user': 0,
            'email_avg_received_per_user': 0,
            
            # Teams Activity
            'teams_active_users': 0,
            'teams_total_meetings': 0,
            'teams_avg_meetings_per_user': 0,
            'teams_avg_messages_per_user': 0,
            
            # OneDrive Usage
            'onedrive_total_accounts': 0,
            'onedrive_active_accounts': 0,
            'onedrive_adoption_rate': 0,
            'onedrive_storage_gb': 0,
            
            # Office Activations
            'activations_total_users': 0,
            'activations_desktop_rate': 0,
            
            # Active Users (Latest Snapshot)
            'office365_active_users': 0,
            'exchange_active_users': 0,
            'teams_active_users_snapshot': 0,
            'sharepoint_active_users': 0,
            'onedrive_active_users': 0
        }
    
    # Extract from pre-computed summaries
    sites_summary = getattr(m365_client, 'sites_summary', {})
    users_summary = getattr(m365_client, 'users_summary', {})
    email_summary = getattr(m365_client, 'email_summary', {})
    teams_summary = getattr(m365_client, 'teams_summary', {})
    sharepoint_summary = getattr(m365_client, 'sharepoint_summary', {})
    onedrive_summary = getattr(m365_client, 'onedrive_summary', {})
    activations_summary = getattr(m365_client, 'activations_summary', {})
    active_users_summary = getattr(m365_client, 'active_users_summary', {})
    
    insights = {
        'available': True,
        
        # Sites & SharePoint
        'total_sites': sites_summary.get('total', 0),
        'site_names': sites_summary.get('site_names', []),
        'sharepoint_report_available': sharepoint_summary.get('available', False),
        'sharepoint_report_period': sharepoint_summary.get('report_period', 'D30'),
        'sharepoint_active_sites': sharepoint_summary.get('active_sites', 0),
        'sharepoint_total_files': sharepoint_summary.get('total_files', 0),
        'sharepoint_total_page_views': sharepoint_summary.get('total_page_views', 0),
        'sharepoint_activity_rate': sharepoint_summary.get('site_activity_rate', 0),
        'sharepoint_avg_files_per_site': sharepoint_summary.get('avg_files_per_site', 0),
        
        # Users & Licensing
        'total_users': users_summary.get('total', 0),
        'enabled_users': users_summary.get('enabled', 0),
        'disabled_users': users_summary.get('disabled', 0),
        'copilot_licensed_users': users_summary.get('copilot_licensed', 0),
        'copilot_adoption_rate': users_summary.get('copilot_adoption_rate', 0),
        'user_data_sampled': users_summary.get('sampled', False),
        
        # Email Activity (Outlook/Exchange) - Parsed Metrics
        'email_report_available': email_summary.get('available', False),
        'email_report_period': email_summary.get('report_period', 'D30'),
        'email_active_users': email_summary.get('active_users', 0),
        'email_total_sent': email_summary.get('total_sent', 0),
        'email_total_received': email_summary.get('total_received', 0),
        'email_total_read': email_summary.get('total_read', 0),
        'email_avg_sent_per_user': email_summary.get('avg_sent_per_user', 0),
        'email_avg_received_per_user': email_summary.get('avg_received_per_user', 0),
        
        # Teams Activity - Parsed Metrics
        'teams_report_available': teams_summary.get('available', False),
        'teams_report_period': teams_summary.get('report_period', 'D30'),
        'teams_active_users': teams_summary.get('active_users', 0),
        'teams_total_meetings': teams_summary.get('total_meetings', 0),
        'teams_total_calls': teams_summary.get('total_calls', 0),
        'teams_total_team_chat_messages': teams_summary.get('total_team_chat_messages', 0),
        'teams_total_private_messages': teams_summary.get('total_private_messages', 0),
        'teams_avg_meetings_per_user': teams_summary.get('avg_meetings_per_user', 0),
        'teams_avg_messages_per_user': teams_summary.get('avg_messages_per_user', 0),
        
        # OneDrive Usage - Parsed Metrics
        'onedrive_report_available': onedrive_summary.get('available', False),
        'onedrive_report_period': onedrive_summary.get('report_period', 'D30'),
        'onedrive_total_accounts': onedrive_summary.get('total_accounts', 0),
        'onedrive_active_accounts': onedrive_summary.get('active_accounts', 0),
        'onedrive_adoption_rate': onedrive_summary.get('adoption_rate', 0),
        'onedrive_total_files': onedrive_summary.get('total_files', 0),
        'onedrive_storage_gb': onedrive_summary.get('storage_used_gb', 0),
        'onedrive_avg_files_per_user': onedrive_summary.get('avg_files_per_user', 0),
        
        # Office Activations - Parsed Metrics
        'activations_report_available': activations_summary.get('available', False),
        'activations_total_users': activations_summary.get('total_users_with_activations', 0),
        'activations_windows_users': activations_summary.get('windows_users', 0),
        'activations_mac_users': activations_summary.get('mac_users', 0),
        'activations_mobile_users': activations_summary.get('mobile_users', 0),
        'activations_desktop_rate': activations_summary.get('desktop_adoption_rate', 0),
        
        # Active Users (Latest Snapshot) - Parsed Metrics
        'active_users_report_available': active_users_summary.get('available', False),
        'active_users_report_period': active_users_summary.get('report_period', 'D30'),
        'office365_active_users': active_users_summary.get('office_365_active', 0),
        'exchange_active_users': active_users_summary.get('exchange_active', 0),
        'teams_active_users_snapshot': active_users_summary.get('teams_active', 0),
        'sharepoint_active_users': active_users_summary.get('sharepoint_active', 0),
        'onedrive_active_users': active_users_summary.get('onedrive_active', 0),
        'yammer_active_users': active_users_summary.get('yammer_active', 0),
        
        # Missing Permissions (for recommendations to flag setup issues)
        'missing_permissions': getattr(m365_client, 'missing_permissions', [])
    }
    
    return insights
