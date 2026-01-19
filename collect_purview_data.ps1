# PowerShell data collector for Purview compliance endpoints
# Collects deployment data via Security & Compliance cmdlets and pipes to main.py
# Usage: .\collect_purview_data.ps1 [-DataOnly]

param(
    [switch]$DataOnly  # If set, outputs JSON only (for Python subprocess invocation)
)

# Check required PowerShell modules
. "$PSScriptRoot\Check-PSModules.ps1"
if (-not (Test-RequiredModules -ScriptType "Purview")) {
    exit 1
}

# Helper function to write output only in interactive mode
function Write-Progress {
    param([string]$Message, [string]$Color = "White", [switch]$NoNewline)
    if (-not $DataOnly) {
        if ($NoNewline) {
            Write-Progress $Message -ForegroundColor $Color -NoNewline
        } else {
            Write-Progress $Message -ForegroundColor $Color
        }
    }
}

if (-not $DataOnly) {
    Write-Progress "================================================================" -ForegroundColor Cyan
    Write-Progress "Purview Data Collection + M365 Readiness Assessment" -ForegroundColor Cyan
    Write-Progress "================================================================" -ForegroundColor Cyan
    Write-Progress ""
}

# Step 1: Connect to M365 Services
if (-not $DataOnly) {
    Write-Progress "[1/4] Connecting to M365 services..." -ForegroundColor Yellow
    Write-Progress "      A browser window will open for authentication" -ForegroundColor Gray
}
try {
    Import-Module ExchangeOnlineManagement -ErrorAction Stop
    
    # Check if already connected to avoid duplicate prompts
    $ippsConnected = $false
    $exoConnected = $false
    
    try {
        # Test IPPS connection
        Get-DlpCompliancePolicy -ErrorAction Stop | Out-Null
        $ippsConnected = $true
        Write-Progress "      → Security & Compliance: Already connected" -ForegroundColor Cyan
    } catch {
        # Not connected, will connect below
    }
    
    try {
        # Test Exchange connection
        Get-OrganizationConfig -ErrorAction Stop | Out-Null
        $exoConnected = $true
        Write-Progress "      → Exchange Online: Already connected" -ForegroundColor Cyan
    } catch {
        # Not connected, will connect below
    }
    
    # Connect only if not already connected
    if (-not $ippsConnected) {
        Write-Progress "      → Connecting to Security & Compliance..." -NoNewline
        Connect-IPPSSession -ErrorAction Stop -WarningAction SilentlyContinue | Out-Null
        Write-Progress " ✓" -ForegroundColor Green
        # Output to stderr so Python can display in real-time
        [Console]::Error.WriteLine("AUTH_COMPLETE:Security & Compliance")
    }
    
    if (-not $exoConnected) {
        # Re-check if Exchange was auto-connected by IPPSSession
        try {
            Get-OrganizationConfig -ErrorAction Stop | Out-Null
            $exoConnected = $true
            # If auto-connected, send message immediately
            [Console]::Error.WriteLine("AUTH_COMPLETE:Exchange Online")
        } catch {
            # Not auto-connected, need to connect manually
            Write-Progress "      → Connecting to Exchange Online..." -NoNewline
            Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop -WarningAction SilentlyContinue | Out-Null
            Write-Progress " ✓" -ForegroundColor Green
            # Output to stderr so Python can display in real-time
            [Console]::Error.WriteLine("AUTH_COMPLETE:Exchange Online")
        }
    } else {
        # Already connected, send confirmation
        [Console]::Error.WriteLine("AUTH_COMPLETE:Exchange Online")
    }
    
    if ($ippsConnected -and $exoConnected) {
        Write-Progress "      ✓ Using existing connections" -ForegroundColor Green
    }
} catch {
    Write-Progress "      ✗ Connection failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Progress ""
    Write-Progress "Please ensure you have:" -ForegroundColor Yellow
    Write-Progress "  - ExchangeOnlineManagement module installed" -ForegroundColor Yellow
    Write-Progress "  - Appropriate permissions for Security & Compliance" -ForegroundColor Yellow
    exit 1
}

# Step 2: Collect Purview data
if (-not $DataOnly) {
    Write-Progress ""
    Write-Progress "[2/4] Collecting Purview compliance data..." -ForegroundColor Yellow
}

$purviewData = @{}
$permissionFailures = @()

# Collect DLP Policies
Write-Progress "      → DLP Compliance Policies..." -NoNewline
try {
    $dlpPolicies = Get-DlpCompliancePolicy -ErrorAction Stop | Select-Object Name, Mode, Enabled, ExchangeLocation, SharePointLocation, OneDriveLocation
    $purviewData['dlp_policies'] = @{
        count = $dlpPolicies.Count
        policies = $dlpPolicies
    }
    Write-Progress " $($dlpPolicies.Count) found" -ForegroundColor Green
} catch {
    Write-Progress " Permission denied" -ForegroundColor Red
    $purviewData['dlp_policies'] = @{ count = 0; policies = @(); permission_denied = $true }
    $permissionFailures += "DLP Policies"
}

# Collect Sensitivity Labels
Write-Progress "      → Sensitivity Labels..." -NoNewline
try {
    $labels = Get-Label -ErrorAction Stop | Select-Object Name, DisplayName, Tooltip, Enabled
    $purviewData['sensitivity_labels'] = @{
        count = $labels.Count
        labels = $labels
    }
    Write-Progress " $($labels.Count) found" -ForegroundColor Green
} catch {
    Write-Progress " Permission denied" -ForegroundColor Red
    $purviewData['sensitivity_labels'] = @{ count = 0; labels = @(); permission_denied = $true }
    $permissionFailures += "Sensitivity Labels"
}

# Collect Retention Policies
Write-Progress "      → Retention Compliance Policies..." -NoNewline
try {
    $retentionPolicies = Get-RetentionCompliancePolicy -ErrorAction Stop | Select-Object Name, Enabled, Type
    $purviewData['retention_policies'] = @{
        count = $retentionPolicies.Count
        policies = $retentionPolicies
    }
    Write-Progress " $($retentionPolicies.Count) found" -ForegroundColor Green
} catch {
    Write-Progress " Permission denied" -ForegroundColor Red
    $purviewData['retention_policies'] = @{ count = 0; policies = @(); permission_denied = $true }
    $permissionFailures += "Retention Policies"
}

# Collect Label Policies
Write-Progress "      → Sensitivity Label Policies..." -NoNewline
try {
    $labelPolicies = Get-LabelPolicy -ErrorAction Stop -WarningAction SilentlyContinue | Select-Object Name, Enabled, Mode
    $purviewData['label_policies'] = @{
        count = $labelPolicies.Count
        policies = $labelPolicies
    }
    Write-Progress " $($labelPolicies.Count) found" -ForegroundColor Green
} catch {
    Write-Progress " Permission denied" -ForegroundColor Red
    $purviewData['label_policies'] = @{ count = 0; policies = @(); permission_denied = $true }
    $permissionFailures += "Label Policies"
}

# Collect Insider Risk Policies
Write-Progress "      → Insider Risk Policies..." -NoNewline
try {
    $insiderRiskPolicies = Get-InsiderRiskPolicy -ErrorAction Stop | Select-Object Name, Enabled, InsiderRiskScenario
    $purviewData['insider_risk_policies'] = @{
        count = $insiderRiskPolicies.Count
        policies = $insiderRiskPolicies
    }
    Write-Progress " $($insiderRiskPolicies.Count) found" -ForegroundColor Green
} catch {
    Write-Progress " Permission denied" -ForegroundColor Red
    $purviewData['insider_risk_policies'] = @{ count = 0; policies = @(); permission_denied = $true }
    $permissionFailures += "Insider Risk Policies"
}

# Collect Communication Compliance Policies
Write-Progress "      → Communication Compliance..." -NoNewline
try {
    $commCompPolicies = Get-SupervisoryReviewPolicyV2 -ErrorAction Stop | Select-Object Name, Enabled, SamplingRate
    $purviewData['communication_compliance'] = @{
        count = $commCompPolicies.Count
        policies = $commCompPolicies
    }
    Write-Progress " $($commCompPolicies.Count) found" -ForegroundColor Green
} catch {
    Write-Progress " Permission denied" -ForegroundColor Red
    $purviewData['communication_compliance'] = @{ count = 0; policies = @(); permission_denied = $true }
    $permissionFailures += "Communication Compliance"
}

# Collect Information Barriers
Write-Progress "      → Information Barriers..." -NoNewline
try {
    $ibPolicies = Get-InformationBarrierPolicy -ErrorAction Stop | Select-Object Name, State, AssignedSegment
    $purviewData['information_barriers'] = @{
        count = $ibPolicies.Count
        policies = $ibPolicies
    }
    Write-Progress " $($ibPolicies.Count) found" -ForegroundColor Green
} catch {
    Write-Progress " Permission denied" -ForegroundColor Red
    $purviewData['information_barriers'] = @{ count = 0; policies = @(); permission_denied = $true }
    $permissionFailures += "Information Barriers"
}

# Collect eDiscovery Cases
Write-Progress "      → eDiscovery Cases..." -NoNewline
try {
    $cases = Get-ComplianceCase -ErrorAction Stop | Select-Object Name, Status, CaseType
    $purviewData['ediscovery_cases'] = @{
        count = $cases.Count
        cases = $cases
    }
    Write-Progress " $($cases.Count) found" -ForegroundColor Green
} catch {
    Write-Progress " Permission denied" -ForegroundColor Red
    $purviewData['ediscovery_cases'] = @{ count = 0; cases = @(); permission_denied = $true }
    $permissionFailures += "eDiscovery Cases"
}

# Collect Organization Configuration
Write-Progress "      → Organization Config..." -NoNewline
try {
    $orgConfig = Get-OrganizationConfig -ErrorAction Stop | Select-Object CustomerLockBoxEnabled, AuditDisabled, IsDehydrated
    $purviewData['org_config'] = $orgConfig
    $lockboxStatus = if ($orgConfig.CustomerLockBoxEnabled) { "Lockbox: Enabled" } else { "Lockbox: Disabled" }
    Write-Progress " $lockboxStatus" -ForegroundColor Green
} catch {
    Write-Progress " Failed" -ForegroundColor Red
    $purviewData['org_config'] = @{}
}

# Collect IRM Configuration
Write-Progress "      → Azure RMS Configuration..." -NoNewline
try {
    $irmConfig = Get-IRMConfiguration -ErrorAction Stop | Select-Object AzureRMSLicensingEnabled, InternalLicensingEnabled
    $purviewData['irm_config'] = $irmConfig
    $rmsStatus = if ($irmConfig.AzureRMSLicensingEnabled) { "RMS: Enabled" } else { "RMS: Disabled" }
    Write-Progress " $rmsStatus" -ForegroundColor Green
} catch {
    Write-Progress " Failed" -ForegroundColor Red
    $purviewData['irm_config'] = @{}
}

# Collect Audit Configuration
Write-Progress "      → Audit Configuration..." -NoNewline
try {
    $auditConfig = Get-AdminAuditLogConfig -ErrorAction Stop | Select-Object UnifiedAuditLogIngestionEnabled, AdminAuditLogEnabled
    $purviewData['audit_config'] = $auditConfig
    $auditStatus = if ($auditConfig.UnifiedAuditLogIngestionEnabled) { "Unified Audit: Enabled" } else { "Unified Audit: Disabled" }
    Write-Progress " $auditStatus" -ForegroundColor $(if ($auditConfig.UnifiedAuditLogIngestionEnabled) { "Green" } else { "Yellow" })
} catch {
    Write-Progress " Failed" -ForegroundColor Red
    $purviewData['audit_config'] = @{}
}

# Step 3: Serialize and output data
if (-not $DataOnly) {
    Write-Progress ""
    if ($permissionFailures.Count -gt 0) {
        Write-Progress "⚠️  Permission denied for $($permissionFailures.Count) data source(s): $($permissionFailures -join ', ')" -ForegroundColor Yellow
        Write-Progress "    License recommendations will still be generated. Deployment recommendations limited." -ForegroundColor Gray
        Write-Progress ""
    }
    Write-Progress "[3/4] Running Python assessment tool..." -ForegroundColor Yellow
    Write-Progress ""
    Write-Progress ""
}

# Convert to JSON
$jsonData = $purviewData | ConvertTo-Json -Depth 10 -Compress

if ($DataOnly) {
    # DataOnly mode: Output JSON to stdout (for Python subprocess)
    Write-Output $jsonData
} else {
    # Interactive mode: Pass data to Python via stdin
    $env:PURVIEW_DATA_SOURCE = "stdin"
    $jsonData | python main.py
    
    Write-Progress ""
    Write-Progress "================================================================" -ForegroundColor Cyan
    Write-Progress "Assessment Complete!" -ForegroundColor Green
    Write-Progress "================================================================" -ForegroundColor Cyan
}
