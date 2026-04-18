$env:PYTHONPATH = "src"

if (Get-Command pytest -ErrorAction SilentlyContinue) {
    pytest -q
    exit $LASTEXITCODE
}

$pythonCandidates = @(
    "C:\Users\gamph\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    ".\.venv\Scripts\python.exe"
)

$pythonCommand = $null
foreach ($candidate in $pythonCandidates) {
    if (Test-Path $candidate) {
        $pythonCommand = $candidate
        break
    }
}

if (-not $pythonCommand) {
    foreach ($commandName in @("python", "py")) {
        if (Get-Command $commandName -ErrorAction SilentlyContinue) {
            $pythonCommand = $commandName
            break
        }
    }
}

if (-not $pythonCommand) {
    Write-Error "Neither pytest nor a Python interpreter is available. Cannot run tests/tier_transition_smoke.py."
    exit 1
}

Write-Host "pytest not found; running tests/tier_transition_smoke.py instead."
& $pythonCommand "tests\tier_transition_smoke.py"
exit $LASTEXITCODE
