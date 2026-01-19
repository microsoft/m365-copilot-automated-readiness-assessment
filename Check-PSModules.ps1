# Check-PSModules.ps1
# Validates that all required PowerShell modules are installed

function Test-ModuleInstalled {
    param([string]$ModuleName)
    return $null -ne (Get-Module -ListAvailable -Name $ModuleName)
}

function Show-ModuleStatus {
    param(
        [string]$ModuleName,
        [bool]$IsInstalled,
        [string]$InstallCommand
    )
    
    if ($IsInstalled) {
        Write-Host "  ✓ " -ForegroundColor Green -NoNewline
        Write-Host "$ModuleName" -ForegroundColor White
    } else {
        Write-Host "  ✗ " -ForegroundColor Red -NoNewline
        Write-Host "$ModuleName" -ForegroundColor White
        Write-Host "    Install: " -ForegroundColor Yellow -NoNewline
        Write-Host $InstallCommand -ForegroundColor Cyan
    }
}

function Test-RequiredModules {
    param([string]$ScriptType)
    
    $modules = @()
    
    # Define module requirements based on script type
    switch ($ScriptType) {
        "Purview" {
            $modules = @(
                @{Name = "ExchangeOnlineManagement"; Install = "Install-Module ExchangeOnlineManagement -Scope CurrentUser"}
            )
        }
        "PowerPlatform" {
            $modules = @(
                @{Name = "Az.Accounts"; Install = "Install-Module Az -Scope CurrentUser"}
            )
        }
        "Setup" {
            $modules = @(
                @{Name = "Microsoft.Graph.Authentication"; Install = "Install-Module Microsoft.Graph -Scope CurrentUser -Force -AllowClobber"}
                @{Name = "Microsoft.Graph.Applications"; Install = "Install-Module Microsoft.Graph -Scope CurrentUser -Force -AllowClobber"}
            )
        }
        "All" {
            $modules = @(
                @{Name = "ExchangeOnlineManagement"; Install = "Install-Module ExchangeOnlineManagement -Scope CurrentUser"}
                @{Name = "Az.Accounts"; Install = "Install-Module Az -Scope CurrentUser"}
                @{Name = "Microsoft.Graph.Authentication"; Install = "Install-Module Microsoft.Graph -Scope CurrentUser -Force -AllowClobber"}
                @{Name = "Microsoft.Graph.Applications"; Install = "Install-Module Microsoft.Graph -Scope CurrentUser -Force -AllowClobber"}
            )
        }
    }
    
    $missingModules = @()
    $allInstalled = $true
    
    Write-Host "Checking PowerShell module dependencies..." -ForegroundColor Cyan
    
    foreach ($module in $modules) {
        $isInstalled = Test-ModuleInstalled -ModuleName $module.Name
        Show-ModuleStatus -ModuleName $module.Name -IsInstalled $isInstalled -InstallCommand $module.Install
        
        if (-not $isInstalled) {
            $allInstalled = $false
            if ($module -notin $missingModules) {
                $missingModules += $module
            }
        }
    }
    
    if (-not $allInstalled) {
        Write-Host "`n❌ ERROR: Missing required PowerShell modules" -ForegroundColor Red
        Write-Host "`nTo install missing modules, run these commands:" -ForegroundColor Yellow
        
        # Get unique install commands
        $uniqueInstalls = $missingModules | Select-Object -Property Install -Unique
        foreach ($cmd in $uniqueInstalls) {
            Write-Host "  $($cmd.Install)" -ForegroundColor Cyan
        }
        
        Write-Host "`nNote: You may need to run PowerShell as Administrator for installation." -ForegroundColor Yellow
        
        return $false
    }
    
    Write-Host "✓ All required PowerShell modules are installed" -ForegroundColor Green
    return $true
}

# If script is run directly (not dot-sourced)
if ($MyInvocation.InvocationName -ne '.') {
    param(
        [Parameter(Mandatory=$false)]
        [ValidateSet("Purview", "PowerPlatform", "Setup", "All")]
        [string]$ScriptType = "All"
    )
    
    $result = Test-RequiredModules -ScriptType $ScriptType
    
    if (-not $result) {
        exit 1
    }
}
