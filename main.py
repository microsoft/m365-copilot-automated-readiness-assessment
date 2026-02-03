import sys
import asyncio

# Check dependencies before proceeding
from Core.check_dependencies import check_dependencies
check_dependencies()

# Setup console encoding for Windows
from Core.console_setup import setup_console_encoding
setup_console_encoding()

# Import common utilities
from Core.spinner import get_timestamp

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
    from Core.orchestrator import orchestrate
    from Core.cli_parser import parse_arguments
    from Core.credentials_check import validate_credentials_or_exit
    
    # Parse command-line arguments
    args = parse_arguments(TENANT_ID, SERVICES)
    
    # Use parsed values (command-line overrides or defaults from params.py)
    tenant_id = args.tenant_id
    services = args.services if args.services else []  # Empty list means all services
    
    # Check for required credentials before starting orchestration
    validate_credentials_or_exit(get_timestamp)
    
    try:
        asyncio.run(orchestrate(tenant_id, services))
    except ValueError as e:
        # Catch credential-related errors gracefully
        error_msg = str(e)
        if "environment variables" in error_msg.lower() or "credentials" in error_msg.lower():
            print(f"\n[{get_timestamp()}] ❌ Authentication error: {error_msg}")
            sys.exit(1)
        raise
    except Exception as e:
        print(f"\n[{get_timestamp()}] ❌ Unexpected error: {e}")
        sys.exit(1)