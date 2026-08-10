# Troubleshooting record template

Copy this file for a diagnostic case. A generic diagnostic idea starts as `Troubleshooting Example`; it is not an experiment incident.

## Evidence classification

- Allowed evidence status: `CONFIRMED` | `PARTIAL_CONFIRMED` | `NOT_VERIFIED`
- Case classification: `Troubleshooting Example` | `Evidence-backed Incident`
- Incident evidence status: `NOT_VERIFIED`
- Date/time:
- Repository commit:
- Sanitized reporter role/ID:
- Sanitized reviewer role/ID:

Keep `Troubleshooting Example` for generic guidance. Select `Evidence-backed Incident` and change the incident evidence status only when an actual run has a source record, sanitized original error and evidence path.

## Context

- Workflow stage:
- Execution mode: `dry_run` | `mock` | `hardware_connection_only` | `hardware`
- Dataset/checkpoint identifier:
- Resolved config evidence path:
- Hardware involved:
- Robot action sent: `NOT_VERIFIED` | `no` | `yes`

## Symptom and evidence

- Symptom:
- Expected behavior:
- Original error or state:
- Sanitized log location:
- Evidence path:
- Reproduction steps:

## Diagnosis

- First failing layer:
- Hypotheses checked:
- Evidence for confirmed cause:
- Root-cause status: `NOT_VERIFIED`
- Confirmed root cause:

## Response and verification

- Immediate safety response:
- Change made:
- Rollback path:
- Regression test:
- Verification result: `NOT_VERIFIED`
- Remaining risks:
- Notes:

Do not infer a hardware incident from CI/Mock output, and do not publish private identifiers, raw logs, video, model files or unsupported metrics.
