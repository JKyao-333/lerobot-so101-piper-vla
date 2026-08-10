# Validation

Run from the repository root:

```bash
python -m compileall -q src scripts
find scripts -type f -name '*.sh' -print0 | xargs -0 -n1 bash -n
pytest -q
make validate
git diff --check
```

`make validate` additionally validates the measured experiment baseline and its workflow projections, executes every hardware-free workflow preview, checks all YAML templates, scans text for sensitive patterns, and rejects files over 20 MB plus common model/dataset/video extensions. It is designed for a host with no robot and no GPU.

Use `python scripts/validate_experiment_baseline.py --json` for a compact machine-readable summary. This confirms provenance and internal consistency only; it does not emit missing task-performance metrics.

Use `python scripts/environment_check.py --profile software --strict` to verify the installed distributions and dual-ACT config semantics. Use `--profile deployment --strict` after creating `.env` to add checkpoint, camera and CAN presence checks. Strict mode returns non-zero for missing, failed or unavailable checks, but a pass is not checkpoint/processors compatibility, camera-stream, CAN-bitrate or hardware-replay evidence. The tool never connects a robot, opens a camera, configures CAN or sends an action.

| Status | Meaning in this repository |
| --- | --- |
| `measured_experiment_baseline` | Run parameters recorded from the completed source experiments |
| `schema_validated` | Configuration format and semantics passed validation |
| `dry_run_verified` | Command construction passed in a dependency-free preview environment |
| `mock_verified` | MockRobot and mock-policy behavior passed tests |
| `ci_verified` | The corresponding GitHub Actions revision passed |
| `source_experiment.hardware_operated` | `true`: the historical source experiment used hardware |
| `repository_revision.hardware_replayed_on_current_commit` | `false`: this refactored commit still needs an end-to-end hardware replay |

The two hardware fields describe different events and must not be collapsed into one ambiguous flag. CI validates software reproducibility without requiring physical robot hardware; it does not change the completed status of the source experiment or claim a current-commit robot replay.

## Documentation contracts

`tests/test_documentation_contracts.py` keeps the deployment documentation aligned with the repository by checking:

- all seven engineering guides are present and linked from README;
- all four evidence templates are linked from `results/README.md` and start with `NOT_VERIFIED` fields;
- local Markdown links resolve to real files;
- dataset-pipeline values match the measured experiment baseline;
- documented script entrypoints exist;
- OpenVLA remains described as LIBERO simulation rather than Piper deployment;
- README preserves the full demonstration-to-training-to-Piper-execution feedback loop;
- the hardware interface inventory remains limited to the five actual module groups;
- Dual ACT design records distinct checkpoints/processors, reset, limits, gates, and tradeoffs;
- the deployment checklist covers pre-, during-, and post-deployment controls;
- generic failure cases remain labeled `Troubleshooting Example`, not experiment observations.
- the environment checker remains linked, read-only and covered by CLI tests.
- the Robot PC bootstrap remains dry-run by default and its source pins match the documented revisions.

These checks catch stale paths and unsupported positioning claims. They do not validate hardware availability, runtime performance, model quality, or physical task success.
