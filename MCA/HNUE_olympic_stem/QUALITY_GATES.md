# QUALITY_GATES.md

Use this file to define the minimum evidence before merge, release, or task completion for HNUE Olympic STEM.

## Default Gates

| Gate | Required For | Evidence |
| --- | --- | --- |
| lint | Code / script changes | Command output or explicit skip reason |
| typecheck | Typed codebases (Python / TS) | Typecheck command output or skip reason |
| unit tests | Logic / algorithm changes | Passing test output (`tests/`) |
| simulation / demo | STEM model, sa bàn, hardware loop | Simulation logs / recorded evidence / photos in `assets/` |
| doc validation | Thuyết minh, poster, slide báo cáo | Proof of compliance with HNUE Olympic STEM rules |
| security review | Credentials / API keys / student PII | Scan for secrets and personal data before publishing |

## Agent Rule

- Never claim completion without matching the task to the relevant gate.
- If a gate cannot run, state why and list residual risk.
- Tất cả báo cáo nghiệm thu phải có bằng chứng cụ thể xuất ra `AE_VALIDATION_REPORT.md`.
