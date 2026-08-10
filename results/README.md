# Results and deployment evidence

This directory is the review entrypoint for experiment and deployment evidence. The source experiments described by the repository were completed, while the current refactored revision has not been replayed end to end on the target hardware. Create a new record for every replay; do not overwrite the preserved source baseline or convert CI/Mock output into hardware evidence.

## Templates

| Template | Use |
| --- | --- |
| [ACT rollout record](act_rollout_record_template.md) | One ACT/SmolVLA single-policy rollout or supervised replay |
| [Dual ACT test record](dual_act_test_record_template.md) | Two-skill state machine, handoff, limits and failure-stage evidence |
| [Deployment record](deployment_record_template.md) | Pre-, during- and post-deployment readiness and rollback evidence |
| [Troubleshooting record](troubleshooting_record_template.md) | A generic troubleshooting example or an evidence-backed incident |
| [Legacy generic result record](result_template.md) | Existing generic quantitative-result review fields |

Every copied template uses the controlled evidence statuses `CONFIRMED`, `PARTIAL_CONFIRMED`, and `NOT_VERIFIED`, and starts as `NOT_VERIFIED`. Change a field to `CONFIRMED` only when the same record contains a reviewable source or sanitized evidence path. Use `PARTIAL_CONFIRMED` only when the supported and missing portions are both explicit.

## Recording workflow

1. Copy the closest template to a new file; do not edit the template itself.
2. Name the record with a date and bounded purpose, for example `YYYYMMDD_act_rollout_<label>.md`.
3. Record the repository commit and dirty state before the run.
4. Run the read-only [environment check](../scripts/environment_check.py) and attach its sanitized output or summary.
5. Fill the exact config, checkpoint identifier, dataset identifier, command and execution mode.
6. Record whether any robot action was sent. Dry-run, MockRobot and CI must stay distinct from hardware execution.
7. Preserve the original outcome and failure stage; do not replace it with a cleanup result.
8. Sanitize evidence, obtain reviewer confirmation and only then publish supported conclusions.

## Publication boundary

Do not commit raw robot logs, private datasets, videos, checkpoints, device serial numbers, account names, endpoints, tokens or local absolute paths. Store large/private evidence outside the public repository and record only a sanitized relative reference or controlled evidence ID.

No success rate, loss, latency, duration or hardware replay result may be filled from expectation, a manual example, dry-run or MockRobot. Quantitative fields without an evidence path, evaluation date, episodes/tasks and source record must remain blank or `NOT_VERIFIED`.
