"""
Command-line argument parser for the Assessment Tool.
"""

import argparse


def parse_arguments(tenant_id_default, services_default):
    """
    Parse command-line arguments for the assessment tool.
    
    Args:
        tenant_id_default: Default tenant ID from params.py
        services_default: Default services list from params.py
        
    Returns:
        argparse.Namespace: Parsed arguments with tenant_id and services
    """
    parser = argparse.ArgumentParser(
        description='Microsoft 365 Copilot and Agents Readiness Assessment Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py
  python main.py --services M365
  python main.py --services M365 Entra Defender
  python main.py --tenant-id "your-tenant-id" --services Purview
        '''
    )
    parser.add_argument(
        '--tenant-id', 
        type=str, 
        default=tenant_id_default,
        help=f'Tenant ID to analyze (default: {tenant_id_default})'
    )
    parser.add_argument(
        '--services', 
        nargs='*', 
        default=services_default,
        help=f'Services to analyze: M365, Entra, Defender, Purview, "Power Platform", "Copilot Studio" (default: {services_default or "all services"})'
    )
    
    return parser.parse_args()
