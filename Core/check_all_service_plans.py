"""
Service plan analysis - shows how many features will be evaluated
"""
import asyncio
from pathlib import Path
from .get_graph_client import get_graph_client
from .service_categorization import determine_service_type

async def analyze_service_plans(tenant_id, services_to_run):
    """
    Analyze service plans and show how many features will be evaluated
    
    Args:
        tenant_id: Azure tenant ID
        services_to_run: List of services to run (from params.py)
    """
    from .spinner import get_timestamp
    import sys
    import time
    
    # Check if we need to analyze Graph-based services (M365, Entra, Defender)
    # Skip for PowerShell-based services (Purview, Power Platform)
    run_all = "all" in [s.lower() for s in services_to_run]
    graph_services = ['m365', 'entra', 'defender', 'copilot_studio']
    needs_graph_analysis = run_all or any(s.lower() in graph_services for s in services_to_run)
    
    if not needs_graph_analysis:
        # No Graph-based services to analyze, skip feature analysis
        return
    
    # Get all service plans from tenant (shows auth messages)
    client = await get_graph_client(tenant_id)
    
    # Start progress bar for data fetching
    start_time = time.time()
    sys.stdout.write(f"[{get_timestamp()}]   Analyzing Features      [{'░' * 20}]   0%")
    sys.stdout.flush()
    
    # Fetch subscription data
    skus = await client.subscribed_skus.get()
    
    # Update to 50% after fetch completes
    elapsed = time.time() - start_time
    filled = int(20 * 0.5)
    bar = '█' * filled + '░' * (20 - filled)
    sys.stdout.write(f"\r[{get_timestamp()}]   Analyzing Features      [{bar}]  50% {elapsed:>6.1f}s")
    sys.stdout.flush()
    
    # Collect all service plans by category
    tenant_plans = {
        'M365': set(),
        'Entra': set(),
        'Defender': set(),
        'Purview': set(),
        'Power Platform': set(),
        'Copilot Studio': set()
    }
    
    # Map display names to folder names
    service_folder_map = {
        'M365': 'm365',
        'Entra': 'entra',
        'Defender': 'defender',
        'Purview': 'purview',
        'Power Platform': 'power_platform',
        'Copilot Studio': 'copilot_studio'
    }
    
    # Count total plans to process
    total_plans = sum(len(sku.service_plans) for sku in skus.value)
    processed = 0
    
    for sku in skus.value:
        for plan in sku.service_plans:
            plan_name = plan.service_plan_name
            service_type = determine_service_type(plan_name)
            
            # Map service_type to display name
            type_to_display = {
                'm365': 'M365',
                'entra': 'Entra',
                'defender': 'Defender',
                'purview': 'Purview',
                'power_platform': 'Power Platform',
                'copilot_studio': 'Copilot Studio'
            }
            
            display_name = type_to_display.get(service_type)
            if display_name in tenant_plans:
                tenant_plans[display_name].add(plan_name.upper())
            
            # Update progress (50% to 100% based on processing)
            processed += 1
            progress = 0.5 + (0.5 * processed / total_plans)
            filled = int(20 * progress)
            bar = '█' * filled + '░' * (20 - filled)
            elapsed = time.time() - start_time
            sys.stdout.write(f"\r[{get_timestamp()}]   Analyzing Features      [{bar}] {int(progress * 100):3d}% {elapsed:>6.1f}s")
            sys.stdout.flush()
    
    # Complete at 100%
    elapsed = time.time() - start_time
    sys.stdout.write(f"\r[{get_timestamp()}]   ✓ Analyzing Features      [{'█' * 20}] 100% {elapsed:>6.1f}s\033[K\n")
    sys.stdout.flush()
    
    # Check which services will run
    run_all = "all" in [s.lower() for s in services_to_run]
    services_to_evaluate = services_to_run if not run_all else list(tenant_plans.keys())
    
    # Get recommendation file counts (Recommendations folder is in project root, not Core)
    base_path = Path(__file__).parent.parent / 'Recommendations'
    
    print(f"📋 Feature Evaluation Summary:")
    print(f"{'='*80}")
    
    total_features = 0
    total_with_files = 0
    
    for service_name in services_to_evaluate:
        if service_name not in service_folder_map:
            continue
            
        folder_name = service_folder_map[service_name]
        folder_path = base_path / folder_name
        
        if not folder_path.exists():
            continue
        
        # Get recommendation files (excluding helpers)
        helper_files = {'m365_insights', 'entra_insights', 'defender_insights', 'purview_insights'}
        recommendation_files = set()
        
        for py_file in folder_path.glob("*.py"):
            if py_file.stem != "__init__" and py_file.stem not in helper_files:
                recommendation_files.add(py_file.stem.upper())
        
        # Get matching plans
        plans_in_tenant = tenant_plans.get(service_name, set())
        matching = recommendation_files & plans_in_tenant
        
        total_features += len(plans_in_tenant)
        total_with_files += len(matching)
        
        status = "✅" if len(matching) == len(plans_in_tenant) else "⚠️"
        print(f"  {status} {service_name:<20} {len(matching):>3} features with recommendations")
    
    print(f"{'='*80}")
    print(f"  Total: {total_with_files} features will be evaluated")
    print(f"{'='*80}")
    print()

def analyze_plans_sync(tenant_id, services):
    """Synchronous wrapper for analyze_service_plans"""
    asyncio.run(analyze_service_plans(tenant_id, services))
