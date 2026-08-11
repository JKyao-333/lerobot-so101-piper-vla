# ACT rollout record template

Copy this file for a new run. The untouched template is not an experiment result.

## Evidence classification

- Allowed evidence status: `CONFIRMED` | `PARTIAL_CONFIRMED` | `NOT_VERIFIED`
- Record status: `NOT_VERIFIED`
- Value origin: `experiment_recorded` | `replayed_on_current_commit` | `derived`
- Execution mode: `NOT_VERIFIED` | `dry_run` | `mock` | `hardware`
- Robot action sent: `NOT_VERIFIED` | `no` | `yes`

## Run identity

- Date/time:
- Repository commit:
- Repository dirty state:
- Sanitized operator role/ID:
- Sanitized reviewer role/ID:

## Environment

- Host role:
- OS:
- Python:
- LeRobot revision/version:
- Piper adapter revision/version:
- Environment-check status:
- Environment-check evidence path:

## Inputs

- Policy type: ACT | SmolVLA
- Checkpoint identifier or sanitized path:
- Checkpoint/processors consistency: `NOT_VERIFIED`
- Dataset identifier or sanitized path:
- Task text:
- Resolved config evidence path:
- Sanitized command:

## Hardware

- Hardware status: `NOT_VERIFIED`
- SO-101 Leader:
- Piper / CAN interface:
- Front camera:
- Wrist camera:
- Physical stop and supervision confirmation:

## Result

- Result status: `NOT_VERIFIED`
- Episodes attempted:
- Final runtime state:
- Failure stage, if any:
- Hold/stop result:
- Sanitized log location:
- Evidence path:
- Notes:

## Quantitative claims

- Success count:
- Success rate:
- Runtime:
- Inference latency:

Leave quantitative fields blank unless the record includes the evaluation date, episode/task count, source record and reviewable evidence path. Dry-run, MockRobot and CI are not hardware rollout evidence.
