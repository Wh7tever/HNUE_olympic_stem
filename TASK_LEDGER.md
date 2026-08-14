# TASK_LEDGER.md
Use this file as the project task ledger across humans, agents, and sessions.
| Task ID | Slice | Status | Owner/Agent | Scope | Files/Modules | Verification | Blocker | Evidence | Interaction Mode | Blocked By |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-0003 | VS-001 | done | AE_Executor | Reclaim 3.42GB sandboxes, standardize .gitignore, maintain 100% RCP health | `RCP_sandboxes`, `.gitignore`, `TASK_LEDGER.md`, `PROJECT_STATUS.md` | Test-RCPHealth 37/37 PASS, sandbox count 0 | none | AE_VALIDATION_REPORT.md | AFK | none |
| T-0002 | VS-001 | done | rcp-runtime | Runtime-created bounded task from RCP task prompt. | TO_BE_FILLED | Run Invoke-ProjectVerificationGate.ps1 -ProjectRoot <project> -Mode final and report evidence. | none | PASS | AFK | none |
| T-0001 | VS-001 | done | rcp-runtime | Runtime-created bounded task from RCP task prompt. | TO_BE_FILLED | Run Invoke-ProjectVerificationGate.ps1 -ProjectRoot <project> -Mode final and report evidence. | none | PASS | AFK | none |

## Status Values
- todo
- doing
- blocked
- review
- done

## Interaction Mode
- AFK: agent can continue without user input.
- HITL: human decision, private access, external action, or product judgment is required.
- unknown: not classified yet.

## Agent Rule
- Claim one task at a time unless explicitly instructed otherwise.
- Do not mark done without verification evidence.
- If blocked, record the blocker and recommended next move.
