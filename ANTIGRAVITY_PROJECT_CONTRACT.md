# Antigravity Engine Contract (RCP)

This project is operated by the Antigravity Engine (via RCP) as a machine runtime, not as optional prompt guidance.

Agent Identity: You are an Operator of the Antigravity Engine. This current project is your target material. You must enforce the Engine's rules (from the RCP root) upon this project.

- **Target Project:** `E:\Antigravity\MCA\HNUE_olympic_stem`
- **Subproject of:** Marie Curie Academy (MCA)
- **Domain:** HNUE Olympic STEM (Olympic STEM Đại học Sư phạm Hà Nội)

Mandatory entrypoints:

```powershell
ag.cmd task -ProjectRoot "E:\Antigravity\MCA\HNUE_olympic_stem" -TaskText "<task>" -Phase start -Apply
ag.cmd command -ProjectRoot "E:\Antigravity\MCA\HNUE_olympic_stem" -CommandText "<command>" -Purpose "<why>"
ag.cmd task -ProjectRoot "E:\Antigravity\MCA\HNUE_olympic_stem" -TaskText "<task>" -Phase final -Apply
```

Execution rules:

- Non-trivial project work must start with `ag.cmd task ... -Phase start -Apply`.
- Non-trivial shell commands should go through `ag.cmd command`.
- Final completion must run `ag.cmd task ... -Phase final -Apply`.
- If final runtime returns `blocked=true`, `overall_status=FAIL`, or command proxy returns `DENIED`, the agent must not claim completion.
- Runtime artifacts must stay under `<project>\.aok-runtime\`.
- RCP root is read-only during normal project work.

Known limitation:

- This contract and Antigravity hooks reduce bypass risk, but they are not OS-level sandboxing. A capable agent with direct shell access can still bypass unless the host enforces hooks/proxy usage.
