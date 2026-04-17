# OPERATOR RUNBOOK

## Purpose

This runbook is for the internal operator/builder who needs to inspect the runtime without treating it as a black box.

## What to check first

### Health
- Is `/health` returning healthy?
- Is `/ready` returning ready?

### Runtime shape
- Is the request going through the expected webhook path?
- Is the route resolved to the expected transport?
- Is the shell response in the expected render mode?

### Coordination
- Which brain is action lead?
- Is support brain present?
- Is hold-for-more-input triggered?
- Is disagreement surfaced or internal only?

### Plurality
- Was a disagreement event written?
- Did both local notes survive?
- Is reconciliation state:
  - remain_open
  - temporary_operational_alignment
  - partial_convergence
  - full_convergence

### Integrity
- Did monitor raise verification caution?
- Is there unresolved disagreement still open?
- Is there operational alignment without epistemic convergence?
- Is there any fake closure risk?

---

## Recommended inspection order

1. check app health
2. inspect latest operator snapshot
3. inspect dashboard snapshot
4. inspect disagreement event
5. inspect reconciliation state
6. inspect routing decision
7. inspect final response surface

---

## Failure patterns to watch

### 1. False completion
Surface says done, but verification boundary is still open.

### 2. Fake consensus
Action lead gets selected and the system behaves as if plurality disappeared.

### 3. Family shortcut
Family signal increases recognition and silently inflates certainty.

### 4. Tool authority leak
Worker/tool output starts behaving like final authority.

### 5. Trace leakage
User channel accidentally sees builder/operator internals.

---

## Operator posture

The operator should not ask only:
- “did it answer?”

The operator should also ask:
- “did it remain within law?”
- “did it preserve disagreement honestly?”
- “did coordination choose action without pretending truth resolution?”
