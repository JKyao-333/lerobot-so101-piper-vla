# Reproducibility

For each private run, record:

- value origin: `manual_reference` or `measured`;
- repository commit and dirty/clean status;
- upstream commits or package versions;
- sanitized resolved configuration and command;
- dataset identity without raw samples or device serials;
- camera names and non-identifying geometry notes;
- policy/checkpoint identity without committing weights;
- environment package summary, attention backend, and offline/online mode;
- result artifact paths and a sanitized metric derivation.

Use `scripts/collect_env.sh` for a minimal sanitized environment summary and `results/result_template.md` for future evidence. Public metrics require the corresponding reviewable log; completed execution alone is not a quantitative result.

`configs/reference/manual_reference.yaml` must retain `hardware_measured: false`. Promote values into a measured result record instead of rewriting their provenance.
