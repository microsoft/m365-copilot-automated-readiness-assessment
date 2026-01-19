import sys
import os
import asyncio
import threading

# Check dependencies before proceeding
from check_dependencies import check_dependencies
check_dependencies()

# Setup console encoding for Windows
from console_setup import setup_console_encoding
setup_console_encoding()

# Import common utilities
from spinner import get_timestamp

if __name__ == "__main__":
    # Show banner FIRST before any imports
    banner_text = "AUTOMATED READINESS ASSESSMENT TOOL FOR MICROSOFT 365 COPILOT AND AGENTS"
    timestamp = get_timestamp()
    full_banner = f"[{timestamp}] {banner_text}"
    separator = "=" * len(full_banner)
    
    print("\n" + separator)
    print(full_banner)
    print(separator)
    print()
    sys.stdout.flush()  # Ensure banner displays before module imports
    
    # Import after banner to avoid delay
    from params import TENANT_ID, SERVICES
    from orchestrator import orchestrate
    from cli_parser import parse_arguments
    
    # Parse command-line arguments
    args = parse_arguments(TENANT_ID, SERVICES)
    
    # Use parsed values (command-line overrides or defaults from params.py)
    tenant_id = args.tenant_id
    services = args.services if args.services else []  # Empty list means all services
    
    asyncio.run(orchestrate(tenant_id, services))