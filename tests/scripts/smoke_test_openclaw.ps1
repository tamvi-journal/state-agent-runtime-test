param(
    [string]$RepoRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Section($text) {
    Write-Host ""
    Write-Host "=== $text ===" -ForegroundColor Cyan
}

function Invoke-EntryPointJson {
    param(
        [string]$PayloadPath
    )

    $raw = Get-Content -Raw $PayloadPath
    $output = $raw | python -m src.integration.openclaw_entrypoint
    if ($LASTEXITCODE -ne 0) {
        throw "Entrypoint process failed with exit code $LASTEXITCODE for $PayloadPath"
    }
    return $output | ConvertFrom-Json
}

Push-Location $RepoRoot
try {
    $results = @()

    Write-Section "Test 1: minimal payload"
    $min = Invoke-EntryPointJson ".\tests\payloads\payload_min.json"
    $minOk = (
        $min.status -eq "ok" -and
        $null -ne $min.final_response -and
        $null -ne $min.baton -and
        $null -ne $min.verification_outcome
    )
    $results += [pscustomobject]@{
        Test = "payload_min.json"
        Expected = "status=ok"
        Actual = $min.status
        Pass = $minOk
    }
    Write-Host ("status: " + $min.status)
    Write-Host ("verification: " + $min.verification_outcome.status)

    Write-Section "Test 2: session payload"
    $session = Invoke-EntryPointJson ".\tests\payloads\payload_session.json"
    $sessionOk = (
        $session.status -eq "ok" -and
        $null -ne $session.session_status_metadata -and
        $null -ne $session.verification_outcome
    )
    $results += [pscustomobject]@{
        Test = "payload_session.json"
        Expected = "status=ok + session_status_metadata"
        Actual = $session.status
        Pass = $sessionOk
    }
    Write-Host ("status: " + $session.status)
    Write-Host ("verification: " + $session.verification_outcome.status)

    Write-Section "Test 3: invalid payload"
    $invalidRaw = Get-Content -Raw ".\tests\payloads\payload_invalid.json"
    $invalidOut = $invalidRaw | python -m src.integration.openclaw_entrypoint
    $invalidJson = $invalidOut | ConvertFrom-Json
    $invalidOk = ($invalidJson.status -eq "error")
    $results += [pscustomobject]@{
        Test = "payload_invalid.json"
        Expected = "status=error"
        Actual = $invalidJson.status
        Pass = $invalidOk
    }
    Write-Host ("status: " + $invalidJson.status)
    if ($null -ne $invalidJson.error) {
        Write-Host ("error_type: " + $invalidJson.error.error_type)
    }

    Write-Section "Summary"
    $results | Format-Table -AutoSize

    $failed = @($results | Where-Object { -not $_.Pass })
    if ($failed.Count -gt 0) {
        Write-Host ""
        Write-Host "Smoke test: FAIL" -ForegroundColor Red
        exit 1
    } else {
        Write-Host ""
        Write-Host "Smoke test: PASS" -ForegroundColor Green
        exit 0
    }
}
finally {
    Pop-Location
}
