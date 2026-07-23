# Measured experiment baseline

`configs/reference/measured_experiment_baseline.yaml` is the source of truth for run parameters recorded in the seven supplied experiment manuals and supplemental code. The user confirms that the underlying SO-101/Piper, ACT, dual-ACT, OpenVLA-LIBERO, and SmolVLA experiments were completed.

This provenance has two deliberately separate layers:

- `source_experiment`: the historical experiment used robot hardware and completed teleoperation, recording, training, evaluation, and rollout.
- `repository_revision`: this engineered revision passed offline, MockRobot, and CI validation, but has not yet been replayed end-to-end on the current hardware environment.

`hardware_replayed_on_current_commit: false` therefore means pending current-revision replay, not that the source experiment was never run on hardware.

## Recorded baseline

| Area | Experiment-recorded configuration | Environment-dependent fields |
| --- | --- | --- |
| Piper transport | 1,000,000 bit/s, gripper enabled, normalized positions | `can0` interface name |
| SO-101 leader | leader id `so101_leader_01` | `/dev/ttyACM0` port |
| Cameras | front/wrist roles, 640x480 at 30 FPS | indices `0` and `2` |
| ACT dataset | 50 episodes, 30 s episode, 15 s reset, 15 FPS, 2 encoder threads, CRF 20 | dataset path and repository id |
| ACT | 20,000-step checkpoint selection | checkpoint and output paths, GPU device |
| Dual ACT | 15 Hz, 35 s skill timeouts, 100 s total, 30 s handoff, 7 actions | checkpoint paths and task text |
| Dual ACT safety | normalized joints `[-95, 95]`, gripper `[0, 100]`, deltas `2` and `4` | robot-specific supervised acceptance |
| OpenVLA | Spatial, Object, Goal, Long and center crop | installed revision, checkpoint location, compute environment |
| SmolVLA Piper | batch 4, workers 4, 20,000 steps, save every 5,000 | model, dataset, output and GPU paths |
| Async inference | 15 Hz, 50 actions/chunk, threshold 0.5, `weighted_average` | cameras, endpoint, tunnel and checkpoint |

These are experiment-recorded configuration and run parameters. They are not automatically portable hardware identities, and they are not substitutes for absent success-rate, loss, latency, duration, or other quantitative evidence.

With the pinned Piper adapter, `use_degrees=false` means joint positions use an approximately `[-100, 100]` normalized representation and the gripper uses `[0, 100]`; these values are not radians. The `[-95, 95]` boundary is a conservative normalized action boundary used in the experiment, not a hardware joint-angle limit.

## Offline validation

```bash
python scripts/validate_experiment_baseline.py
python scripts/validate_experiment_baseline.py --json
make workflow-dry-run
python scripts/run_dual_act.py \
  --config configs/dual_act/dual_act.example.yaml \
  --auto-confirm-mock
```

These commands validate provenance, configuration projections, command construction, and mock behavior without hardware. They do not replay the source experiment or prove current-host ports, cameras, CUDA capacity, checkpoint compatibility, collision clearance, or task performance.

Before any execute flag, verify every device port, camera identifier, CAN interface and bitrate, task text, dataset and checkpoint path, network endpoint, cloud directory, GPU device, and installed upstream revision. Follow [hardware onboarding](hardware_onboarding.md) and record a new replay separately with `results/result_template.md`; do not overwrite the source baseline.
