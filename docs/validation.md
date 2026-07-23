# Validation

Run from the repository root:

```bash
python -m compileall -q src scripts
find scripts -type f -name '*.sh' -print0 | xargs -0 -n1 bash -n
pytest -q
make validate
git diff --check
```

`make validate` additionally validates the manual example profile and its workflow projections, executes every hardware-free workflow preview, checks all YAML templates, scans text for sensitive patterns, and rejects files over 20 MB plus common model/dataset/video extensions. It is designed for a host with no robot and no GPU.

Use `python scripts/validate_reference_profile.py --json` for a compact machine-readable summary. This confirms internal consistency only; it does not emit task-success metrics.

| Status | Meaning in this repository |
| --- | --- |
| `manual_example` | Course-manual values used only for configuration and workflow reference |
| `schema_validated` | Configuration format and semantics passed validation |
| `dry_run_verified` | Command construction passed in a dependency-free preview environment |
| `mock_verified` | MockRobot and mock-policy behavior passed tests |
| `ci_verified` | The corresponding GitHub Actions revision passed |
| `hardware_measured` | Must remain `false` in the public manual example profile |
| `hardware_verified` | Must not be claimed for the current repository |

Only the first five statuses may be claimed after their checks pass. None of them means current-host verification, robot execution verification, or measured performance.
