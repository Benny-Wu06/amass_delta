# pc_scanner.ps1
# Scans this Windows PC for installed software and OS version,
# then POSTs the inventory to the amass_delta vulnerability backend.
#
# Usage:
#   .\pc_scanner.ps1                     # POST results to backend
#   .\pc_scanner.ps1 -SaveOnly           # Save scan_results.json locally (upload via web UI)
#   .\pc_scanner.ps1 -BackendUrl <url>   # Override the API endpoint

param(
    [string]$BackendUrl = "https://2r5sbcl74l.execute-api.ap-southeast-2.amazonaws.com/v1/scan/match",
    [switch]$SaveOnly
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Scanning this PC for installed software..." -ForegroundColor Cyan

# --- OS info ---
$os = Get-WmiObject Win32_OperatingSystem
$osInfo = @{
    name    = $os.Caption
    version = $os.Version
    build   = $os.BuildNumber.ToString()
}

Write-Host "  OS: $($osInfo.name) (build $($osInfo.build))"

# --- Installed programs (registry) ---
$regPaths = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$seen    = @{}
$software = @()

foreach ($path in $regPaths) {
    $items = Get-ItemProperty $path -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        $name = ($item.DisplayName -replace '^\s+|\s+$', '')
        if (-not $name -or $seen[$name]) { continue }
        $seen[$name] = $true

        $software += [ordered]@{
            name      = $name
            version   = if ($item.DisplayVersion) { $item.DisplayVersion.Trim() } else { "unknown" }
            publisher = if ($item.Publisher)       { $item.Publisher.Trim()      } else { "unknown" }
        }
    }
}

Write-Host "  Found $($software.Count) installed programs."

# --- Assemble inventory ---
$inventory = [ordered]@{
    os         = $osInfo
    software   = $software
    scanned_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$json = $inventory | ConvertTo-Json -Depth 5 -Compress

# --- Output ---
if ($SaveOnly) {
    $json | Out-File -FilePath "scan_results.json" -Encoding utf8
    Write-Host "Saved to scan_results.json. Upload this file in the amass_delta PC Scanner page." -ForegroundColor Green
} else {
    Write-Host "Sending inventory to backend..." -ForegroundColor Cyan
    try {
        $bytes    = [System.Text.Encoding]::UTF8.GetBytes($json)
        $response = Invoke-RestMethod -Uri $BackendUrl -Method POST `
                      -Body $bytes -ContentType "application/json" -ErrorAction Stop
        $resultJson = $response | ConvertTo-Json -Depth 10
        Write-Host "Scan complete. Results:" -ForegroundColor Green
        Write-Host $resultJson
        # Also save a local copy for reference
        $resultJson | Out-File -FilePath "scan_results.json" -Encoding utf8
        Write-Host "Results also saved to scan_results.json" -ForegroundColor Gray
    } catch {
        Write-Host "POST failed: $_" -ForegroundColor Red
        Write-Host "Saving inventory locally as scan_results_inventory.json instead." -ForegroundColor Yellow
        $json | Out-File -FilePath "scan_results_inventory.json" -Encoding utf8
        Write-Host "Upload scan_results_inventory.json via the amass_delta PC Scanner page." -ForegroundColor Yellow
    }
}
