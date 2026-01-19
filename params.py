TENANT_ID = "92be237d-7eaa-4f11-be0e-0d87ca6abf1e"  # e.g., 'contoso.onmicrosoft.com' or GUID

# Services to analyze - valid values: "M365", "Entra", "Defender", "Purview", "Power Platform", "Copilot Studio"
# Empty array = analyze all services
# Note: "Defender" includes Copilot-specific security recommendations (Security Posture, Threat Intelligence, Data Governance)
#       Copilot Data Governance recommendation will also use Purview data if available (run with: .\collect_purview_data.ps1)
SERVICES = ["Defender"]  # e.g., ["M365", "Entra"], ["Defender", "Purview"], or [] for all