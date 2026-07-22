# Validation

Run from the repository root:

```bash
python -m compileall -q src scripts
find scripts -type f -name '*.sh' -print0 | xargs -0 -n1 bash -n
pytest -q
make validate
git diff --check
```

`make validate` additionally checks all YAML templates, scans text for sensitive patterns, and rejects files over 20 MB plus common model/dataset/video extensions. It is designed for a host with no robot and no GPU.

