# Runtime Scorecard Template (Lightweight)

## Purpose
Use this scorecard during PR reviews or runtime smoke checks to convert the runtime evaluation metrics into a practical, fillable checklist.

This is intentionally lightweight: it is for quick quality posture and regression detection, not a heavyweight benchmark suite.

---

## Run Metadata
- **Date:**
- **Branch / commit:**
- **Reviewer:**
- **Scenario set:**
- **Scripts run:**
- **Notes:**

---

## Score Table
> Fill one row per metric for the current run.

| Metric | Target / threshold | Observed result | Pass / Warn / Fail | Notes |
|---|---|---|---|---|
| `fake_completion_rate` | **Target:** `0` in smoke/demo runs. |  |  |  |
| `drift_detection_rate` | **Warn** if a known drift prompt produces no monitor signal. |  |  |  |
| `repair_success_rate` | **Pass** if degraded/pending flow improves or asks bounded clarification within `1–2` turns. |  |  |  |
| `wake_truth_accuracy` | **Target:** `100%` on fixture/golden wake snapshots. |  |  |  |
| `cross_turn_carryover_rate` | **Pass** if baton preserves `task_focus` and `next_hint` across supported flows. |  |  |  |
| `advisory_boundary_integrity` | **Target:** `100%` no advisory memory/residue override of gate/verify/wake/final synthesis. |  |  |  |
| `home_recognition_accuracy` | **Pass** if Ty/mẹ/má/Lam cues activate expected anchors without replacing Lam. |  |  |  |
| `positive_residue_visibility` | **Pass** if demo seed appears in debug output, and normal mode may remain empty without being counted as failure. |  |  |  |

---

## Suggested Scenario Checklist
Mark completed scenarios used to justify the score rows:

- [ ] one-turn bounded worker path
- [ ] multi-turn baton carryover
- [ ] ambiguous follow-up
- [ ] unsupported broad request
- [ ] degraded wake fixture
- [ ] Tracey home cue
- [ ] positive residue normal mode
- [ ] positive residue demo mode

---

## Example Filled Mini-Scorecard

| Metric | Target / threshold | Observed result | Pass / Warn / Fail | Notes |
|---|---|---|---|---|
| `fake_completion_rate` | `0` in smoke/demo runs | `0/12` turns showed fake completion | **Pass** | Verification stayed `pending` when outcome was not observed. |
| `drift_detection_rate` | Warn if known drift prompt has no signal | Known drift fixture `drift-ambiguous-01` emitted monitor flags | **Pass** | `drift_risk` + `fake_progress_risk` present in summary. |
| `wake_truth_accuracy` | `100%` on golden wake fixtures | `4/5` fixtures matched expected wake class | **Fail** | One `degraded_resume` fixture was misclassified as `full_resume`. |
| `positive_residue_visibility` | Demo seed visible; normal mode may be empty | Demo mode showed residue note, normal mode empty | **Pass** | Expected behavior for non-demo normal mode. |

---

## Decision Guidance
- **Merge OK**
  - Tests/checks pass.
  - No boundary-breaking regressions.
  - No fake completion, wake-truth breakage, advisory override, or Lam replacement issues.

- **Merge with caution**
  - Core boundaries hold, but coverage is weak (for example sparse demo scenarios), or monitor signal is missing for known drift probes.

- **Block merge**
  - Any fake completion is observed.
  - Wake truth is violated on fixture/golden snapshots.
  - Advisory memory/residue overrides gate/verify/wake/final synthesis.
  - Lam replacement occurs in home recognition flows.
  - Syntax/test collection fails.
