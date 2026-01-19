from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
import httpx
import logging
import os

# Suppress Azure SDK warnings
logging.getLogger('azure.identity').setLevel(logging.ERROR)

# Load .env file into environment variables (no external dependency)
def _load_env():
    """Load .env file if it exists"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables on import
_load_env()

# Module-level cache for clients
_graph_client = None
_credential = None

async def get_graph_client(tenant_id=None, silent=False):
    """Get Microsoft Graph SDK client using service principal authentication
    
    Args:
        tenant_id: Azure tenant ID (optional)
        silent: If True, suppress authentication messages (for background license checks)
    
    Args:
        tenant_id: Azure tenant ID (optional, read from .env if not provided)
        
    Returns:
        GraphServiceClient instance
    """
    global _graph_client, _credential
    
    if _graph_client:
        return _graph_client
    
    # Get credentials from environment
    tenant_id = tenant_id or os.getenv('TENANT_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    
    if not all([tenant_id, client_id, client_secret]):
        raise ValueError(
            "Missing required environment variables. Ensure .env file contains:\n"
            "  TENANT_ID=<your-tenant-id>\n"
            "  CLIENT_ID=<your-app-id>\n"
            "  CLIENT_SECRET=<your-client-secret>\n"
            "Run setup-service-principal.ps1 to create these credentials."
        )
    
    from spinner import get_timestamp
    if not silent:
        print(f"[{get_timestamp()}] ℹ️     Authenticating with service principal...")
        import sys
        sys.stdout.flush()
    
    # Create credential using service principal
    if _credential is None:
        _credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    
    # Create Graph client
    _graph_client = GraphServiceClient(
        credentials=_credential,
        scopes=['https://graph.microsoft.com/.default']
    )
    
    if not silent:
        print(f"[{get_timestamp()}] ✅ Authenticated successfully")
        import sys
        sys.stdout.flush()
    return _graph_client

def get_shared_credential():
    """Get shared credential for non-Graph APIs (Defender, Power Platform)
    
    Returns:
        ClientSecretCredential instance
    """
    global _credential
    
    if _credential is not None:
        return _credential
    
    # Get credentials from environment
    tenant_id = os.getenv('TENANT_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    
    if not all([tenant_id, client_id, client_secret]):
        raise ValueError("Missing credentials in .env file. Run setup-service-principal.ps1 first.")
    
    _credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    
    return _credential

def get_power_platform_credential():
    """Get credential for Power Platform APIs
    
    Returns the same shared credential (service principal).
    
    Returns:
        ClientSecretCredential instance
    """
    return get_shared_credential()

async def get_api_client(service_name):
    """Get HTTP client with bearer token for specific API
    
    Args:
        service_name: One of 'defender', 'power_platform'
    
    Returns:
        httpx.AsyncClient with authorization header
    """
    credential = get_shared_credential()
    
    # Define scopes and base URLs for each service
    service_config = {
        'defender': {
            'scope': 'https://api.security.microsoft.com/.default',
            'base_url': 'https://api.security.microsoft.com'
        },
        'power_platform': {
            'scope': 'https://service.powerapps.com/.default',
            'base_url': 'https://service.powerapps.com'
        }
    }
    
    if service_name not in service_config:
        raise ValueError(f"Unknown service: {service_name}. Valid: {list(service_config.keys())}")
    
    config = service_config[service_name]
    
    # Get token for the specific scope (synchronous call)
    token = credential.get_token(config['scope'])
    
    # Create HTTP client with bearer token
    return httpx.AsyncClient(
        base_url=config['base_url'],
        headers={
            "Authorization": f"Bearer {token.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        timeout=30.0
    )
