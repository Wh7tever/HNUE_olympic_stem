# PROJECT_PROFILE.md

This file classifies the project so agents choose the right structure, toolkit, and verification depth.

## Classification

- project_name: HNUE_olympic_stem
- project_type: automation
- project_size: small
- stack: unknown
- risk_level: low
- data_sensitivity: internal
- production_status: local_only
- team_mode: solo

## Recommended Operating Mode

- recommended_toolkit: AI_Agent_Operating_Kit_Lite for easy/clear tasks; Full when ambiguity appears
- recommended_model_policy: GPT-5.5 medium by default; GPT-5.5 extra high only for reasoning gates.

## Size Rules

- tiny: local script, simple tool, or very small UI with minimal risk.
- small: real repo with a few flows, low-medium risk, and maintainability needs.
- standard: multi-feature project with auth/data/module boundaries or long-running maintenance.
- enterprise: production-risk project with sensitive data, permissions, migrations, release/rollback, or incident needs.

## Agent Rule

- If observed project reality is larger or riskier than this profile, report the mismatch before side effects.
- If project_size is `standard` or `enterprise`, prefer the Full toolkit for planning, review, and cross-module work.
