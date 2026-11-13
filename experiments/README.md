# Experiments

Use this folder for prototypes, spikes, and failed ideas that should not pollute production code.

## Rules

- Keep experiments isolated from `src/` unless explicitly promoted.
- Record the hypothesis, result, and decision.
- Preserve useful failed attempts so agents do not repeat known-bad paths.
- Do not store secrets, customer data, production credentials, or private security details here.

## Suggested Structure

```text
experiments/
  YYYY-MM-DD-short-topic/
    README.md
    prototype/
    notes.md
```

## Experiment README Template

```md
# Experiment: Short Topic

Date: YYYY-MM-DD
Owner: TO_BE_FILLED
Status: exploring | failed | promoted | archived

## Hypothesis
What are we trying to learn?

## Method
What was built or tested?

## Result
What happened?

## Decision
Promote, retry later, or discard?

## Reusable Lessons
- TO_BE_FILLED
```

## Agent Rule

- Check experiments only when the current task touches a similar design, prototype, or failed path.
- Do not load all experiments by default.
