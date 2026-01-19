# PowerShell data collector for Power Platform & Copilot Studio
# Collects deployment data via Power Platform Management APIs for both services
# This unified collector serves both Power Platform and Copilot Studio pipelines
# Usage: .\collect_power_platform_and_copilot_studio_data.ps1 [-DataOnly] [-TenantId <guid>]

param(
    [switch]$DataOnly,  # If set, outputs JSON only (for Python subprocess invocation)
    [string]$TenantId   # Azure AD Tenant ID
)

# Set buffer width to prevent line wrapping issues when called from Python
if ($DataOnly) {
    $host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size(120, 3000)
}

# Check required PowerShell modules
. "$PSScriptRoot\Check-PSModules.ps1"
if (-not (Test-RequiredModules -ScriptType "PowerPlatform")) {
    exit 1
}

# Helper function to write output only in interactive mode
function Write-ConditionalOutput {
    param([string]$Message, [string]$Color = "White", [switch]$NoNewline)
    if (-not $DataOnly) {
        if ($NoNewline) {
            Write-Host $Message -ForegroundColor $Color -NoNewline
        } else {
            Write-Host $Message -ForegroundColor $Color
        }
    }
}

if (-not $DataOnly) {
    Write-ConditionalOutput "================================================================" -Color Cyan
    Write-ConditionalOutput "Power Platform & Copilot Studio Data Collection" -Color Cyan
    Write-ConditionalOutput "================================================================" -Color Cyan
    Write-ConditionalOutput ""
}

# Step 1: Connect to Power Platform
Write-ConditionalOutput "[1/3] Connecting to Power Platform APIs..." -Color Yellow
Write-ConditionalOutput "      Device authentication will be used (follow instructions below)" -Color Gray

# Validate tenant ID
if (-not $TenantId) {
    Write-ConditionalOutput "      X TenantId parameter is required" -Color Red
    Write-ConditionalOutput "      Usage: .\collect_power_platform_data.ps1 -TenantId <guid>" -Color Yellow
    exit 1
}

try {
    # Check if already connected
    $connected = $false
    try {
        # Test connection by trying to get tenant details (lightweight call)
        $testCall = Invoke-RestMethod -Uri "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2023-06-01" `
            -Method Get `
            -Headers @{Authorization = "Bearer $((Get-AzAccessToken -ResourceUrl 'https://api.bap.microsoft.com' -WarningAction SilentlyContinue).Token)"} `
            -ErrorAction Stop
        $connected = $true
        Write-ConditionalOutput "      > Already connected to Power Platform" -Color Cyan
        [Console]::Error.WriteLine("AUTH_COMPLETE:Power Platform")
    } catch {
        # Not connected, need to authenticate
    }
    
    if (-not $connected) {
        Write-ConditionalOutput "" 
        Write-ConditionalOutput "      > Authenticating to Azure (Tenant: $TenantId)..." -Color Cyan
        Write-ConditionalOutput "" 
        
        # Connect to Azure account using device code authentication
        # This works reliably in subprocess scenarios
        # Do NOT pipe to Out-Null - we need to see the device code!
        Connect-AzAccount -Tenant $TenantId -UseDeviceAuthentication -ErrorAction Stop -WarningAction SilentlyContinue
        
        Write-ConditionalOutput "" 
        Write-ConditionalOutput "      > Authentication successful!" -Color Green
        [Console]::Error.WriteLine("AUTH_COMPLETE:Power Platform")
    }
    
} catch {
    Write-ConditionalOutput "      X Connection failed: $($_.Exception.Message)" -Color Red
    Write-ConditionalOutput ""
    Write-ConditionalOutput "Please ensure you have:" -Color Yellow
    Write-ConditionalOutput "  - Az PowerShell module installed (Install-Module Az)" -Color Yellow
    Write-ConditionalOutput "  - Power Platform Administrator role assigned" -Color Yellow
    exit 1
}

# Step 2: Collect Power Platform data
Write-ConditionalOutput ""
Write-ConditionalOutput "[2/3] Collecting Power Platform deployment data..." -Color Yellow

# Get access tokens for Power Platform APIs
$bapToken = (Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com" -WarningAction SilentlyContinue).Token
$flowToken = (Get-AzAccessToken -ResourceUrl "https://service.flow.microsoft.com" -WarningAction SilentlyContinue).Token

$powerPlatformData = @{}
$permissionFailures = @()

# Helper function for API calls
function Invoke-PowerPlatformApi {
    param(
        [string]$Uri,
        [string]$Token
    )
    try {
        $response = Invoke-RestMethod -Uri $Uri -Method Get -Headers @{
            Authorization = "Bearer $Token"
            "Content-Type" = "application/json"
            Accept = "application/json"
        } -ErrorAction Stop
        return $response
    } catch {
        return $null
    }
}

# Collect Environments
Write-ConditionalOutput "      > Environments..." -NoNewline
try {
    $environments = Invoke-PowerPlatformApi `
        -Uri "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2023-06-01" `
        -Token $bapToken
    
    if ($environments) {
        $powerPlatformData["environments"] = $environments.value
        Write-ConditionalOutput " $($environments.value.Count) found" -Color Green
        
        # Get first environment for subsequent calls
        $envName = $environments.value[0].name
    } else {
        throw "No environments returned"
    }
} catch {
    Write-ConditionalOutput " Permission denied" -Color Red
    $powerPlatformData["environments"] = @()
    $permissionFailures += "Environments"
    $envName = $null
}

# Only collect additional data if we have an environment
if ($envName) {
    # Collect Flows
    Write-ConditionalOutput "      > Power Automate Flows..." -NoNewline
    try {
        $flows = Invoke-PowerPlatformApi `
            -Uri "https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple/scopes/admin/environments/$envName/v2/flows?api-version=2016-11-01" `
            -Token $flowToken
        
        if ($flows) {
            $powerPlatformData["flows"] = $flows.value
            Write-ConditionalOutput " $($flows.value.Count) found" -Color Green
        } else {
            throw "No flows returned"
        }
    } catch {
        Write-ConditionalOutput " Permission denied" -Color Red
        $powerPlatformData["flows"] = @()
        $permissionFailures += "Flows"
    }
    
    # Collect Canvas Apps
    Write-ConditionalOutput "      > Canvas Apps..." -NoNewline
    try {
        $envIdForApps = $envName -replace '-', ''
        $apps = Invoke-PowerPlatformApi `
            -Uri "https://$envIdForApps.environment.api.powerplatform.com/powerapps/apps?api-version=1" `
            -Token $bapToken
        
        if ($apps) {
            $powerPlatformData["apps"] = $apps.value
            Write-ConditionalOutput " $($apps.value.Count) found" -Color Green
        } else {
            throw "No apps returned"
        }
    } catch {
        Write-ConditionalOutput " Permission denied" -Color Red
        $powerPlatformData["apps"] = @()
        $permissionFailures += "Apps"
    }
    
    # Collect Connections
    Write-ConditionalOutput "      > Connections..." -NoNewline
    try {
        $connections = Invoke-PowerPlatformApi `
            -Uri "https://api.bap.microsoft.com/providers/Microsoft.PowerApps/scopes/admin/environments/$envName/connections?api-version=2016-11-01" `
            -Token $bapToken
        
        if ($connections) {
            $powerPlatformData["connections"] = $connections.value
            Write-ConditionalOutput " $($connections.value.Count) found" -Color Green
        } else {
            throw "No connections returned"
        }
    } catch {
        Write-ConditionalOutput " Permission denied" -Color Red
        $powerPlatformData["connections"] = @()
        $permissionFailures += "Connections"
    }
    
    # Collect DLP Policies
    Write-ConditionalOutput "      > DLP Policies..." -NoNewline
    try {
        $dlpPolicies = Invoke-PowerPlatformApi `
            -Uri "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/environments/$envName/dlpPolicies?api-version=2024-05-01" `
            -Token $bapToken
        
        if ($dlpPolicies) {
            $powerPlatformData["dlp_policies"] = $dlpPolicies.value
            Write-ConditionalOutput " $($dlpPolicies.value.Count) found" -Color Green
        } else {
            throw "No DLP policies returned"
        }
    } catch {
        Write-ConditionalOutput " Permission denied" -Color Red
        $powerPlatformData["dlp_policies"] = @()
        $permissionFailures += "DLP Policies"
    }
    
    # Collect AI Models
    Write-ConditionalOutput "      > AI Models..." -NoNewline
    try {
        $aiModels = Invoke-PowerPlatformApi `
            -Uri "https://api.bap.microsoft.com/providers/Microsoft.PowerApps/environments/$envName/aiModels?api-version=2024-05-01" `
            -Token $bapToken
        
        if ($aiModels) {
            $powerPlatformData["ai_models"] = $aiModels.value
            Write-ConditionalOutput " $($aiModels.value.Count) found" -Color Green
        } else {
            throw "No AI models returned"
        }
    } catch {
        Write-ConditionalOutput " Permission denied" -Color Red
        $powerPlatformData["ai_models"] = @()
        $permissionFailures += "AI Models"
    }
    
    # Collect Solutions
    Write-ConditionalOutput "      > Solutions..." -NoNewline
    try {
        $solutions = Invoke-PowerPlatformApi `
            -Uri "https://api.bap.microsoft.com/providers/Microsoft.PowerApps/scopes/admin/environments/$envName/solutions?api-version=2016-11-01" `
            -Token $bapToken
        
        if ($solutions) {
            $powerPlatformData["solutions"] = $solutions.value
            Write-ConditionalOutput " $($solutions.value.Count) found" -Color Green
        } else {
            throw "No solutions returned"
        }
    } catch {
        Write-ConditionalOutput " Permission denied" -Color Red
        $powerPlatformData["solutions"] = @()
        $permissionFailures += "Solutions"
    }
} else {
    # No environment available - set empty data
    $powerPlatformData["flows"] = @()
    $powerPlatformData["apps"] = @()
    $powerPlatformData["connections"] = @()
    $powerPlatformData["dlp_policies"] = @()
    $powerPlatformData["ai_models"] = @()
    $powerPlatformData["solutions"] = @()
}

# Step 3: Serialize and output data
if (-not $DataOnly) {
    Write-ConditionalOutput ""
    if ($permissionFailures.Count -gt 0) {
        $failureList = $permissionFailures -join ", "
        Write-ConditionalOutput "Warning: Permission denied for $($permissionFailures.Count) data sources: $failureList" -Color Yellow
        Write-ConditionalOutput "    License recommendations will still be generated. Deployment recommendations limited." -Color Gray
        Write-ConditionalOutput ""
    }
    Write-ConditionalOutput "[3/3] Running Python assessment tool..." -Color Yellow
    Write-ConditionalOutput ""
    Write-ConditionalOutput ""
}

# Convert to JSON
$jsonData = $powerPlatformData | ConvertTo-Json -Depth 10 -Compress

if ($DataOnly) {
    # DataOnly mode: Output JSON to stdout (for Python subprocess)
    Write-Output $jsonData
} else {
    # Interactive mode: Pass data to Python via stdin
    $env:POWER_PLATFORM_DATA_SOURCE = "stdin"
    $jsonData | python main.py
    
    Write-ConditionalOutput ""
    Write-ConditionalOutput "================================================================" -Color Cyan
    Write-ConditionalOutput "Assessment Complete!" -Color Green
    Write-ConditionalOutput "================================================================" -Color Cyan
}


