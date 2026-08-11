# Result record

- Value origin: `experiment_recorded` | `replayed_on_current_commit` | `derived` | `reference_from_upstream`
- Source experiment date:
- Source material:
- Repository commit:
- Hardware:
- Dataset:
- Checkpoint:
- Configuration:
- Evaluation suite:
- Episodes/tasks:
- Success count:
- Success rate:
- Training loss:
- Run duration:
- Latency:
- Evidence path:
- Reviewer:
- Notes:

Use `experiment_recorded` for the preserved source baseline. Create a separate `replayed_on_current_commit` record after a new hardware run; never overwrite the source record. CI and MockRobot results are software validation, not hardware results. Leave every quantitative field blank unless its evidence path and source record are available.
