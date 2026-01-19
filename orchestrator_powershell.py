"""PowerShell subprocess management for orchestrator."""

import os
import sys
import subprocess
import threading
import time
from spinner import get_timestamp, _stdout_lock


async def collect_power_platform_data(tenant_id, run_power_platform, run_copilot_studio):
    """Launch unified Power Platform/Copilot Studio data collector.
    
    This ensures single authentication and data sharing between both services.
    Sets environment variables that will be consumed by service pipelines.
    
    Args:
        tenant_id: Azure tenant ID
        run_power_platform: Whether Power Platform service is requested
        run_copilot_studio: Whether Copilot Studio service is requested
    """
    # Check if data already collected (avoid re-launch)
    if os.environ.get("POWER_PLATFORM_DATA_SOURCE"):
        return
    
    # Launch unified collector
    ps_script_path = os.path.join(os.path.dirname(__file__), "collect_power_platform_and_copilot_studio_data.ps1")
    
    process = subprocess.Popen(
        ["pwsh", "-File", ps_script_path, "-DataOnly", "-TenantId", tenant_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1
    )
    
    # Spinner control
    spinner_stop_event = threading.Event()
    
    def run_spinner(message):
        """Display a rotating spinner with message"""
        spinner_chars = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
        idx = 0
        while not spinner_stop_event.is_set():
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   {spinner_chars[idx]} {message}')
                sys.stdout.flush()
            idx = (idx + 1) % len(spinner_chars)
            time.sleep(0.1)
    
    def stop_spinner():
        """Stop and clear spinner"""
        spinner_stop_event.set()
        if spinner_thread.is_alive():
            spinner_thread.join(timeout=0.5)
        with _stdout_lock:
            sys.stdout.write('\r' + ' ' * 120 + '\r')
            sys.stdout.flush()
    
    # Determine spinner message based on which services are running
    if run_power_platform and run_copilot_studio:
        spinner_message = 'Collecting Power Platform & Copilot Studio data...'
    elif run_power_platform:
        spinner_message = 'Collecting Power Platform data...'
    else:  # run_copilot_studio only
        spinner_message = 'Collecting Copilot Studio data...'
    
    # Start spinner
    spinner_thread = threading.Thread(target=run_spinner, args=(spinner_message,), daemon=True)
    spinner_thread.start()
    
    # Stream output for real-time device code display
    stderr_lines = []
    stdout_lines = []
    
    def stderr_thread_func(process):
        try:
            for line in iter(process.stderr.readline, ''):
                if not line:
                    break
                stderr_lines.append(line.strip())
        except Exception:
            pass
    
    def stdout_thread_func(process):
        try:
            full_output = []
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                full_output.append(line)
                line_stripped = line.rstrip()
                # Display non-JSON output in real-time
                if line_stripped and not line_stripped.startswith('{'):
                    stop_spinner()
                    with _stdout_lock:
                        sys.stdout.write(f'{line_stripped}\n')
                        sys.stdout.flush()
            stdout_lines.extend([l.rstrip() for l in full_output])
        except Exception:
            pass
    
    stderr_thread = threading.Thread(target=stderr_thread_func, args=(process,))
    stderr_thread.daemon = True
    stderr_thread.start()
    
    stdout_thread = threading.Thread(target=stdout_thread_func, args=(process,))
    stdout_thread.daemon = True
    stdout_thread.start()
    
    # Wait for completion
    process.wait()
    stop_spinner()
    stderr_thread.join(timeout=1.0)
    stdout_thread.join(timeout=1.0)
    
    # Extract JSON from stdout
    json_output = ''
    for line in reversed(stdout_lines):
        if line.startswith('{'):
            json_output = line
            break
    
    if json_output and process.returncode == 0:
        # Set environment variables for both services to consume
        os.environ["POWER_PLATFORM_DATA_SOURCE"] = "subprocess"
        os.environ["POWER_PLATFORM_DATA_JSON"] = json_output
        with _stdout_lock:
            sys.stdout.write(f'[{get_timestamp()}]   ✓ Data collection complete\n')
            sys.stdout.flush()
    elif process.returncode != 0:
        with _stdout_lock:
            sys.stdout.write(f'[{get_timestamp()}]   ✗ Data collection failed (will use basic recommendations)\n')
            sys.stdout.flush()


async def collect_purview_data_via_powershell():
    """Launch PowerShell to collect Purview data with interactive authentication.
    
    Sets environment variables that will be consumed by get_purview_client.
    
    Returns:
        bool: True if data collection succeeded, False otherwise
    """
    with _stdout_lock:
        sys.stdout.write(f'[{get_timestamp()}]   ℹ️  Launching PowerShell to collect Purview data (requires interactive auth)...\n')
        sys.stdout.write(f'[{get_timestamp()}]   ⚠️  Browser authentication windows will appear twice (Security & Compliance, then Exchange Online)\n')
        sys.stdout.write(f'[{get_timestamp()}]   ⚠️  Check if browser window is hidden behind other apps/screens\n')
        sys.stdout.flush()
    
    # Invoke collect_purview_data.ps1 in DataOnly mode with real-time stderr streaming
    ps_script = os.path.join(os.path.dirname(__file__), 'collect_purview_data.ps1')
    process = subprocess.Popen(
        ['pwsh', '-File', ps_script, '-DataOnly'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1  # Line buffered
    )
    
    # Spinner control
    spinner_stop_event = threading.Event()
    current_spinner_message = None
    
    def run_spinner(message):
        """Display a rotating spinner with message"""
        spinner_chars = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
        idx = 0
        while not spinner_stop_event.is_set():
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   {spinner_chars[idx]} {message}')
                sys.stdout.flush()
            idx = (idx + 1) % len(spinner_chars)
            time.sleep(0.1)
    
    spinner_thread = None
    
    def start_spinner(message):
        """Start spinner with given message"""
        nonlocal spinner_thread, current_spinner_message
        current_spinner_message = message
        spinner_stop_event.clear()
        spinner_thread = threading.Thread(target=run_spinner, args=(message,), daemon=True)
        spinner_thread.start()
    
    def stop_spinner():
        """Stop and clear spinner"""
        nonlocal spinner_thread
        if spinner_thread and spinner_thread.is_alive():
            spinner_stop_event.set()
            spinner_thread.join(timeout=0.5)
            with _stdout_lock:
                # Clear the spinner line
                sys.stdout.write('\r' + ' ' * 120 + '\r')
                sys.stdout.flush()
    
    # Start spinner for first authentication
    start_spinner('Waiting for Security & Compliance authentication...')
    
    # Stream stderr in real-time to show authentication progress
    def stream_stderr():
        try:
            for line in process.stderr:
                line = line.strip()
                if line.startswith('AUTH_COMPLETE:'):
                    service = line.split(':', 1)[1]
                    stop_spinner()
                    with _stdout_lock:
                        sys.stdout.write(f'[{get_timestamp()}]   ✅ {service} authentication accepted\n')
                        # After Security & Compliance, prompt for Exchange Online
                        if 'Security & Compliance' in service:
                            sys.stdout.write(f'[{get_timestamp()}]   ⚠️  Please provide credentials for Exchange Online authentication...\n')
                            sys.stdout.flush()
                            # Start spinner for Exchange Online auth
                            start_spinner('Waiting for Exchange Online authentication...')
                        else:
                            sys.stdout.flush()
        except ValueError:
            # Pipe closed, thread can exit
            pass
    
    stderr_thread = threading.Thread(target=stream_stderr, daemon=True)
    stderr_thread.start()
    
    # Wait for process to complete and get stdout (don't use communicate())
    stdout = process.stdout.read()
    process.wait()
    result_returncode = process.returncode
    
    # Stop any remaining spinner
    stop_spinner()
    
    # Give stderr thread time to finish processing remaining lines
    stderr_thread.join(timeout=2.0)
    
    if result_returncode != 0:
        with _stdout_lock:
            sys.stdout.write(f'[{get_timestamp()}]   ✗ PowerShell data collection failed\n')
            sys.stdout.flush()
        return False
    
    # Parse JSON output from PowerShell
    import json
    try:
        # Extract just the JSON from the output (ignore warnings/banners)
        stdout_text = stdout.strip()
        # Find the JSON object (starts with { and ends with })
        json_start = stdout_text.find('{')
        json_end = stdout_text.rfind('}')
        if json_start >= 0 and json_end >= 0:
            json_str = stdout_text[json_start:json_end + 1]
            purview_data = json.loads(json_str)
            # Inject data for get_purview_client to consume
            os.environ['PURVIEW_DATA_SOURCE'] = 'subprocess'
            os.environ['PURVIEW_DATA_JSON'] = json_str
            
            with _stdout_lock:
                sys.stdout.write(f'\r[{get_timestamp()}]   ✓ Purview Data Gathering  [████████████████████] 100%\n')
                sys.stdout.flush()
            return True
        else:
            raise ValueError("No JSON found in PowerShell output")
    except (json.JSONDecodeError, ValueError) as e:
        with _stdout_lock:
            sys.stdout.write(f'[{get_timestamp()}]   ✗ Failed to parse PowerShell output: {e}\n')
            sys.stdout.flush()
        return False
