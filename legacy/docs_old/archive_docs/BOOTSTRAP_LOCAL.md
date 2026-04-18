# Bootstrap Local

## 1. Activate venv

PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

bash:
```bash
source .venv/bin/activate
```

## 2. Install dev dependencies

PowerShell:
```powershell
./scripts/bootstrap_dev_env.ps1
```

bash:
```bash
bash ./scripts/bootstrap_dev_env.sh
```

## 3. Run tests

PowerShell:
```powershell
./scripts/test_local.ps1
```

bash:
```bash
bash ./scripts/test_local.sh
```

## 4. Run app locally

PowerShell:
```powershell
./scripts/run_app_local.ps1
```

bash:
```bash
bash ./scripts/run_app_local.sh
```

## 5. Environment

Copy:

```text
config/env.example
```

into your own local env workflow if needed.

## Notes

This phase does not add Docker yet.
It only makes local bootstrap predictable and repeatable.
