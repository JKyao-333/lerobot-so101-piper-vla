# Reproducibility

For each private run, record:

- value origin: `experiment_recorded`, `replayed_on_current_commit`, `derived`, or `reference_from_upstream`;
- repository commit and dirty/clean status;
- upstream commits or package versions;
- sanitized resolved configuration and command;
- dataset identity without raw samples or device serials;
- camera names and non-identifying geometry notes;
- policy/checkpoint identity without committing weights;
- environment package summary, any backend reported by the installed upstream revision, and offline/online mode;
- result artifact paths and a sanitized metric derivation.

Use `scripts/collect_env.sh` for a minimal sanitized environment summary, `scripts/environment_check.py` for scoped prerequisite checks, and `results/README.md` for evidence templates. Public metrics require the corresponding reviewable log; completed execution alone is not a quantitative result.

`configs/reference/measured_experiment_baseline.yaml` preserves the completed source experiment. A new hardware run creates a separate `replayed_on_current_commit` record and must not overwrite the source provenance. CI and MockRobot evidence belongs to repository-revision validation, not a robot result.
