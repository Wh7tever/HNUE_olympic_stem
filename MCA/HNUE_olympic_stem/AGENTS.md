# AGENTS.md

This file is the project-local operating contract for AI agents.

## Project Identity

- Project name: HNUE_olympic_stem
- Project type: automation
- Project size: small
- Stack: unknown

## AOK Operating Mode

- Use the provided AI_Agent_Operating_Kit scenario as the active task contract.
- Read this file before changing project code.
- Keep context bounded: read `PROJECT_MAP.md` and `CONTEXT.md` first when present, then only the relevant modules/files.
- Prefer small, reversible changes with explicit verification evidence.

## Model And Quota Policy

- Allowed project models: GPT-5.5 medium and GPT-5.5 extra high only.
- Daily default: GPT-5.5 medium.
- Use GPT-5.5 extra high only at reasoning gates: initial architecture/planning, hard debugging, ambiguous cross-module work, sensitive/production-risk work, and final audit.
- After the reasoning gate is resolved, step back down to GPT-5.5 medium for implementation and routine verification.
- Do not route project work to any other model.
- At the start of every task, tell the user the recommended model and why. If extra high is only needed for a gate, also say when to switch back to medium.
- Use Lite only for easy and clearly scoped tasks. Escalate to Full when ambiguity, risk, or dependency spread appears.

## Delivery Operating Gate

- For non-trivial work, create or update a bounded work item before implementation: `tools/New-ProjectWorkItem.ps1` or `tools/Update-ProjectWorkItem.ps1` from the attached AOK toolkit.
- Use `TASK_LEDGER.md` as the task ledger and `TASKS/*.md` as per-task execution records.
- `PROJECT_STATUS.md` is auto-synced by the AOK work-item tools; run `tools/Sync-ProjectStatus.ps1` only after hand-editing delivery files.
- At implementation checkpoints, run `tools/Invoke-ProjectOperatingGate.ps1 -ProjectRoot <project> -Mode checkpoint -ProjectSize auto` when local tool execution is available.
- Before claiming done, merge, release, or handoff, run `tools/Invoke-ProjectOperatingGate.ps1 -ProjectRoot <project> -Mode final -ProjectSize auto`.
- If the final gate fails, do not claim completion. Report the gate failure, residual risks, and next actions.

## Allowed Actions

- Read source code, tests, local docs, package metadata, and generated build logs needed for the task.
- Edit code and docs inside this project when the active scenario permits implementation.
- Run local lint, test, typecheck, build, and non-destructive inspection commands.
- Create implementation plans, task-run notes, handoff capsules, or review reports when they reduce risk.

## Ask Before

- Installing or upgrading dependencies.
- Running migrations, deploys, release commands, destructive filesystem commands, data deletion, or bulk rewrites.
- Reading private/security-sensitive folders or files not needed for the current task.
- Accessing production systems, secrets, cloud resources, billing, databases, or external connectors.
- Changing architecture, auth, payment, permission, encryption, backup, or data-retention behavior.

## Production Plugin Safety

- Vercel, Cloudflare, Neon, Sentry, GitHub, Cloudinary, and similar production-capable plugins are read-only by default.
- Before create/update/delete/deploy/rollback/migrate actions, explain the exact target, blast radius, rollback path, and wait for explicit user confirmation in chat.
- Never expose or store secrets in generated docs or research logs.

## Private Context

- Treat secrets, credentials, security notes, customer data, production logs, and private vault pages as sensitive.
- If sensitive context is relevant, ask before reading it and state why it is needed.
- Summarize sensitive findings without copying secrets.

## Build And Test Commands

- Install: `TO_BE_FILLED`
- Dev: `TO_BE_FILLED`
- Build: `TO_BE_FILLED`
- Test: `TO_BE_FILLED`
- Lint: `TO_BE_FILLED`

## Code Quality Standard

- Preserve module boundaries and public contracts.
- Prefer clear names, small functions, direct control flow, and boring maintainable code.
- Do not replace diagnosis with refactoring.
- Add or update tests when behavior changes.
- After edits, report changed files, verification commands, residual risks, and any skipped checks.

## Project Docs To Check

- `PROJECT_MAP.md`: high-level structure and ownership map.
- `CONTEXT.md`: domain language, shared terms, relationships, and ambiguous vocabulary.
- `ARCHITECTURE.md`: architecture decisions and invariants, if present.
- `RUNBOOK.md`: setup, development, verification, and deployment notes, if present.
- `SECURITY_NOTES.md`: sensitive rules and review gates, if present.
- `docs/decisions/`: ADR-style project decisions, if present.
- `experiments/`: prototypes and failed ideas, if present.
- `DELIVERY_PLAN.md`, `TASK_LEDGER.md`, and `PROJECT_STATUS.md`: delivery control plane, if present.
- `requirements/`, `docs/diagrams/`, and enterprise operations docs only when project size requires them.
