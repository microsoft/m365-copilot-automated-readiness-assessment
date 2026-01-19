"""
Dependency checker for Microsoft 365 Copilot Readiness Assessment Tool.
Validates that all required Python packages are installed before execution.
"""

import sys


def check_dependencies():
    """Check if all required Python packages are installed."""
    required_packages = {
        'azure.identity': 'azure-identity',
        'azure.core': 'azure-core',
        'msgraph': 'msgraph-sdk',
        'httpx': 'httpx',
        'openpyxl': 'openpyxl'
    }
    
    missing_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("\n❌ ERROR: Missing required Python packages")
        print("\nThe following packages need to be installed:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\nTo install all dependencies, run:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        print(f"  pip install {' '.join(missing_packages)}")
        sys.exit(1)
