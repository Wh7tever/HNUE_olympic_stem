# Architecture Decision Records

Use this folder for project decisions that future developers or agents must understand.

## When To Add A Decision

- Add an ADR only when the decision is hard to reverse, surprising without written context, or has a real tradeoff future work may question.
- Typical examples: public contract change, module boundary change, dependency/framework/database/deployment/security-model choice.
- Do not create ADRs for routine implementation details, obvious refactors, or reversible local choices.

## File Naming

- `ADR-0001-short-title.md`
- Keep numbering stable once published.

## ADR Template

```md
# ADR-0001: Title

Date: YYYY-MM-DD
Status: proposed | accepted | superseded

## Context
What problem or constraint forced the decision?

## Decision
What did we choose?

## Alternatives Considered
- Option A: tradeoff
- Option B: tradeoff

## Consequences
- Positive:
- Negative:
- Revisit when:
```

## Agent Rule

- Read relevant ADRs before changing architecture, contracts, data model, deployment, security, or module boundaries.
- Do not silently overwrite an ADR. Create a new ADR that supersedes the old one.
