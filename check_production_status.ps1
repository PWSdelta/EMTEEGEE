# EMTEEGEE Production Status Checker - PowerShell Version
# Quickly check if Django and the Enhanced Swarm API are running on production

param(
    [string]$BaseUrl = "https://mtgabyss.com"
)

Write-Host "=== EMTEEGEE PRODUCTION STATUS CHECK ===" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host ""

function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Name,
        [string]$ExpectedType = "any"
    )
    
    Write-Host "🔍 Testing $Name`: $Url" -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            if ($ExpectedType -eq "json") {
                try {
                    $jsonData = $response.Content | ConvertFrom-Json
                    Write-Host "✅ $Name`: OK (JSON response)" -ForegroundColor Green
                    return $true, $jsonData
                }
                catch {
                    Write-Host "⚠️  $Name`: Responding but not valid JSON" -ForegroundColor Yellow
                    return $false, $null
                }
            }
            else {
                Write-Host "✅ $Name`: OK (HTTP 200)" -ForegroundColor Green
                return $true, $response.Content.Substring(0, [Math]::Min(100, $response.Content.Length))
            }
        }
        else {
            Write-Host "❌ $Name`: HTTP $($response.StatusCode)" -ForegroundColor Red
            return $false, $null
        }
    }
    catch {
        if ($_.Exception.Message -like "*502*") {
            Write-Host "❌ $Name`: 502 Bad Gateway (Django not running)" -ForegroundColor Red
        }
        elseif ($_.Exception.Message -like "*timeout*") {
            Write-Host "❌ $Name`: Connection timeout" -ForegroundColor Red
        }
        else {
            Write-Host "❌ $Name`: Error - $($_.Exception.Message)" -ForegroundColor Red
        }
        return $false, $null
    }
}

# Define endpoints to test
$endpoints = @(
    @{ Url = "$BaseUrl/"; Name = "Main Site"; Type = "html" },
    @{ Url = "$BaseUrl/admin/"; Name = "Django Admin"; Type = "html" },
    @{ Url = "$BaseUrl/api/enhanced_swarm/status"; Name = "Enhanced API Status"; Type = "json" },
    @{ Url = "$BaseUrl/api/enhanced_swarm/workers"; Name = "Enhanced API Workers"; Type = "json" },
    @{ Url = "$BaseUrl/api/enhanced_swarm/metrics"; Name = "Enhanced API Metrics"; Type = "json" },
    @{ Url = "$BaseUrl/api/work/get-work"; Name = "Original API (if exists)"; Type = "json" }
)

$results = @{}

# Test each endpoint
foreach ($endpoint in $endpoints) {
    $success, $data = Test-Endpoint -Url $endpoint.Url -Name $endpoint.Name -ExpectedType $endpoint.Type
    $results[$endpoint.Name] = $success
    
    if ($success -and $endpoint.Type -eq "json" -and $data) {
        $jsonPreview = ($data | ConvertTo-Json -Depth 2).Substring(0, [Math]::Min(200, ($data | ConvertTo-Json -Depth 2).Length))
        Write-Host "   📄 Data preview: $jsonPreview..." -ForegroundColor Gray
    }
    Write-Host ""
}

# Summary
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
$workingCount = ($results.Values | Where-Object { $_ -eq $true }).Count
$totalCount = $results.Count

foreach ($result in $results.GetEnumerator()) {
    $status = if ($result.Value) { "✅ WORKING" } else { "❌ FAILED" }
    $color = if ($result.Value) { "Green" } else { "Red" }
    Write-Host "$status`: $($result.Key)" -ForegroundColor $color
}

Write-Host "`n📊 Overall Status: $workingCount/$totalCount endpoints working" -ForegroundColor Cyan

if ($results["Enhanced API Status"]) {
    Write-Host "`n🚀 READY FOR WORKERS: You can now start universal workers!" -ForegroundColor Green
    Write-Host "   Command: python universal_worker_enhanced.py --server $BaseUrl" -ForegroundColor Gray
}
else {
    Write-Host "`n⚠️  NOT READY: Enhanced API is not responding. Django may not be running." -ForegroundColor Yellow
    Write-Host "   Solutions:" -ForegroundColor Gray
    Write-Host "   1. SSH to production server and run: bash deploy_production.sh" -ForegroundColor Gray
    Write-Host "   2. Or manually restart Django on the production server" -ForegroundColor Gray
    Write-Host "   3. Check Django logs for errors" -ForegroundColor Gray
}

Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
Write-Host "If Django is not running on production:" -ForegroundColor Yellow
Write-Host "1. SSH to your production server" -ForegroundColor Gray
Write-Host "2. cd /var/www/emteegee" -ForegroundColor Gray
Write-Host "3. bash deploy_production.sh" -ForegroundColor Gray
Write-Host "4. Run this script again to verify" -ForegroundColor Gray
