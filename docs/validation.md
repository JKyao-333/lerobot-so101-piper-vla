# Validation

Run from the repository root:

```bash
python -m compileall -q src scripts
find scripts -type f -name '*.sh' -print0 | xargs -0 -n1 bash -n
pytest -q
make validate
git diff --check
```

`make validate` additionally validates the trusted manual-reference profile and its workflow projections, checks all YAML templates, scans text for sensitive patterns, and rejects files over 20 MB plus common model/dataset/video extensions. It is designed for a host with no robot and no GPU.

Use `python scripts/validate_reference_profile.py --json` for a compact machine-readable summary. This confirms internal consistency only; it does not emit task-success metrics.
