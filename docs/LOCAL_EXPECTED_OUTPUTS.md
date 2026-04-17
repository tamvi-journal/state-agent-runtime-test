# Local Expected Outputs

## Health
Example:
```json
{
  "ok": true,
  "status": "healthy"
}
```

## Ready
Example:
```json
{
  "ok": true,
  "status": "ready"
}
```

## Telegram webhook
Expected high-level shape:
```json
{
  "accepted": true,
  "status": "accepted",
  "reason": "webhook payload parsed and routed successfully",
  "outbound_message": {
    "transport": "telegram",
    "destination_id": "777",
    "payload": {
      "chat_id": "777",
      "text": "..."
    }
  }
}
```

## Operator latest
Expected high-level shape:
```json
{
  "operator_snapshot": {...},
  "dashboard_snapshot": {...},
  "rendered_console": "[operator-console] ..."
}
```

## Debug runtime shape
Expected high-level keys:
```json
{
  "runtime_shape": {
    "has_final_response": true,
    "has_routing": true,
    "has_reconciliation": true,
    "has_child_result": true,
    "has_governance_output": true,
    "has_context_view": true
  },
  "notes": [...]
}
```

## What does NOT need to be exact yet
At this phase, these may vary:
- exact final response wording
- exact lead/support result
- exact reconciliation state
- whether worker payload is present on every text

What matters more:
- shape is present
- route survives
- boundary chain stays intact
