# Dual ACT test record template

Copy this file for a new two-skill test. Do not fill an expected outcome as an executed result.

## Evidence classification

- Allowed evidence status: `CONFIRMED` | `PARTIAL_CONFIRMED` | `NOT_VERIFIED`
- Record status: `NOT_VERIFIED`
- Execution mode: `NOT_VERIFIED` | `mock` | `hardware_connection_only` | `hardware`
- Robot action sent: `NOT_VERIFIED` | `no` | `yes`

## Run identity

- Date/time:
- Repository commit:
- Repository dirty state:
- Sanitized operator role/ID:
- Sanitized reviewer role/ID:

## Skill A

- Task:
- Checkpoint identifier or sanitized path:
- Preprocess/postprocess verification: `NOT_VERIFIED`
- Completion condition:
- Timeout:

## Skill B

- Task:
- Checkpoint identifier or sanitized path:
- Preprocess/postprocess verification: `NOT_VERIFIED`
- Completion condition:
- Timeout:

## Orchestration and safety

- Handoff method:
- Handoff answer/result:
- Handoff timeout:
- Total timeout:
- Action dimension:
- Absolute action limits:
- Step-delta limits:
- Execution config authorization:
- `--execute-robot` authorization:

## Result

- Run result: `NOT_VERIFIED`
- Final state: `NOT_VERIFIED` | `DONE` | `ABORTED`
- Completed stages:
- Failure stage:
- Original failure reason:
- Hold/stop result:
- Sanitized log location:
- Evidence path:
- Notes:

Mock completion confirms state-machine behavior only. A hardware result requires explicit action authorization, operator supervision, a commit identifier and sanitized evidence.
