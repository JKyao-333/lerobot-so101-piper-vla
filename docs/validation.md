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
