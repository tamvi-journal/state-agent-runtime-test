$base = "http://127.0.0.1:8000"

Write-Host "== health =="
Invoke-RestMethod -Method GET -Uri "$base/health"

Write-Host "== ready =="
Invoke-RestMethod -Method GET -Uri "$base/ready"

$payload = @{
    update_id = 10001
    message = @{
        message_id = 501
        text = "/builder inspect current run"
        chat = @{ id = 777 }
        from = @{
            id = "openclaw"
            username = "openclaw"
            first_name = "OpenClaw"
        }
    }
} | ConvertTo-Json -Depth 6

Write-Host "== telegram webhook =="
Invoke-RestMethod -Method POST -Uri "$base/webhooks/telegram" -ContentType "application/json" -Body $payload

Write-Host "== operator latest =="
Invoke-RestMethod -Method GET -Uri "$base/operator/latest"

Write-Host "== operator session =="
Invoke-RestMethod -Method GET -Uri "$base/operator/session"

Write-Host "== debug runtime shape =="
Invoke-RestMethod -Method GET -Uri "$base/debug/runtime-shape"

Write-Host "== debug run sample =="
Invoke-RestMethod -Method GET -Uri "$base/debug/run-sample"
