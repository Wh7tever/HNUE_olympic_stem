# PROJECT_MAP.md — Workspace Subprojects Map (`E:\Antigravity`)

This file provides AI agents and developers with a clear map of the top-level workspace and its subprojects.

## Summary

- Workspace Root: `E:\Antigravity`
- Primary Control Plane: `Antigravity_engine`
- Total Subprojects: 9
- Domain context: see `CONTEXT.md`

## Top-Level Structure & Subprojects

| Subproject Path | Purpose / Domain | Tech Stack / Entry Point |
| --- | --- | --- |
| `Antigravity_engine/` | Operating Engine & Control Plane for AI Agents | PowerShell, Python, `ag.cmd` |
| `ExamPro/` | Exam creation, LaTeX rendering & Word export web app | React, Vite, Supabase |
| `MarieCurie_Portal/` | School web portal (Admissions, Timetable, News, Admin) | HTML5, CSS3, JavaScript |
| `Preschool_MCA/` | Interactive preschool lessons & teaching media | HTML5, CSS, JS |
| `Chuan_van_ban/` | Administrative document formatting & SSO reports | Automation, Docs |
| `LMS_Support_Extension/` | Browser extension for LMS integration | JavaScript, Chrome Extension API |
| `MCA/` | Class scheduling solver & timetable management | Data processing, HTML |
| `System admin/` | School network, Ruijie Reyee, Hikvision CCTV & OS tuning | PowerShell, ReyeeOS, NVR 5.0 |
| `gdrive_downloader_extension/` | Chrome extension for Google Drive downloads | Manifest v3, JavaScript |

## Module Boundaries & Governance

- Each subproject operates independently in its own subdirectory.
- All AI operations across `E:\Antigravity\*` are governed by `Antigravity_engine` via `ag.cmd task`.
- Do not mix sysadmin scripts or application source code across subproject boundaries.
