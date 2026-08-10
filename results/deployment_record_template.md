# Deployment record template

Copy this file for one bounded deployment attempt. The initial status is `NOT_VERIFIED`.

Allowed evidence status: `CONFIRMED` | `PARTIAL_CONFIRMED` | `NOT_VERIFIED`.

## Deployment identity

- Date/time:
- Repository commit:
- Repository dirty state:
- Target task:
- Sanitized operator role/ID:
- Sanitized reviewer role/ID:
- Overall status: `NOT_VERIFIED`
- Execution mode: `dry_run` | `mock` | `hardware_connection_only` | `hardware`

## Pre-deployment

| Check | Status | Evidence or note |
| --- | --- | --- |
| Python environment | `NOT_VERIFIED` | |
| Dependencies/revisions | `NOT_VERIFIED` | |
| Config file | `NOT_VERIFIED` | |
| Checkpoint paths | `NOT_VERIFIED` | |
| Checkpoint processors | `NOT_VERIFIED` | |
| Front/wrist cameras | `NOT_VERIFIED` | |
| CAN interface and bitrate | `NOT_VERIFIED` | |
| Physical stop and supervision | `NOT_VERIFIED` | |
| Environment-check report | `NOT_VERIFIED` | |

## During deployment

| Check | Status | Evidence or note |
| --- | --- | --- |
| Wrapper dry-run reviewed | `NOT_VERIFIED` | |
| MockRobot/state machine | `NOT_VERIFIED` | |
| Runtime/checkpoint load | `NOT_VERIFIED` | |
| Observation keys/dimensions | `NOT_VERIFIED` | |
| Action limits reviewed | `NOT_VERIFIED` | |
| Action execution authorization | `NOT_VERIFIED` | |
| Robot action sent | `NOT_VERIFIED` | |
| Runtime final state | `NOT_VERIFIED` | |

## Post-deployment

| Check | Status | Evidence or note |
| --- | --- | --- |
| Sanitized log preserved | `NOT_VERIFIED` | |
| Robot final state checked | `NOT_VERIFIED` | |
| Client/server processes stopped | `NOT_VERIFIED` | |
| Hold/stop result recorded | `NOT_VERIFIED` | |
| Rollback target identified | `NOT_VERIFIED` | |
| Evidence reviewed | `NOT_VERIFIED` | |

## Rollback and conclusion

- Rollback trigger:
- Known-good checkpoint/config identifier:
- Rollback action taken:
- Final conclusion:
- Evidence path:
- Remaining `NOT_VERIFIED` items:

Dry-run, MockRobot and CI evidence cannot change a hardware item to `CONFIRMED`.
