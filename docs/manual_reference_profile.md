# Manual reference profile

`configs/reference/manual_reference.yaml` is the single source of truth for values copied from the seven course manuals and the supplied dual-ACT reference implementation. The user has confirmed that these example values are representative enough for configuration, documentation, and hardware-free rehearsal.

The profile deliberately declares `hardware_measured: false`. It is trusted input, not a claim that this repository has connected to the user's current robot, trained a checkpoint, or measured a success rate.

## Selected baseline scenario

- Single skill: `Put the banana on the plate.`
- Long horizon: place the banana on the plate, place a block in the storage box, then return to Home Pose.
- Skill A reuses the single-skill instruction; skill B performs block storage and return.

The long-horizon choice follows the desktop-organization task in `ACT长程任务实践说明.pdf` and the two-independent-checkpoint pattern in `Piper双ACT长程任务实践手册.pdf`.

## Trusted values

| Area | Reference values | Source |
| --- | --- | --- |
| Piper transport | `can0`, 1,000,000 bit/s, gripper enabled, radians/normalized mode | SO101 Piper ACT manual |
| SO-101 leader | `/dev/ttyACM0`, `so101_leader_01` | SO101 Piper ACT manual |
| Cameras | front `0`, wrist `2`, 640x480 at 30 FPS | SO101 Piper ACT and dual ACT manuals |
| ACT dataset | 50 episodes, 30 s episode, 15 s reset, 15 FPS, 2 encoder threads, CRF 20 | SO101 Piper ACT manual |
| ACT checkpoint | 20,000-step reference path; batch and save defaults remain LeRobot-version controlled | SO101 Piper ACT manual |
| Dual ACT | 15 Hz, 35 s per-skill timeout, 100 s total, 30 s handoff, 7 actions | Piper dual ACT manual and supplied script |
| Dual ACT safety | joints `[-95, 95]`, gripper `[0, 100]`, step deltas `2` and `4` | Piper dual ACT manual and supplied script |
| OpenVLA | Spatial, Object, Goal and Long checkpoints; center crop enabled | OpenVLA LIBERO manual |
| SmolVLA Piper | batch 4, workers 4, 20,000 steps, save every 5,000 steps | SmolVLA teaching manual |
| Async inference | 15 Hz, 50 actions/chunk, threshold 0.5, weighted average; nominal 3.333 s | SmolVLA teaching manual |
| SmolVLA LIBERO option | 25,000 steps, save every 5,000, 10 episodes/task, serial evaluation | SmolVLA LIBERO extension manual |

The ACT manuals explicitly leave batch size and save cadence version-dependent. Those two values therefore remain `default_from_lerobot`; the 20,000-step checkpoint is a reference selection, not proof of convergence.

## Hardware-free use

Validate the source profile and all workflow-facing projections:

```bash
python scripts/validate_reference_profile.py
python scripts/validate_reference_profile.py --json
```

Run the dual-ACT state machine against `MockRobot`:

```bash
python scripts/run_dual_act.py \
  --config configs/dual_act/dual_act.example.yaml \
  --auto-confirm-mock
```

`--auto-confirm-mock` is rejected whenever `--hardware` is present, so it cannot bypass the real handoff confirmation.

Preview shell workflows without installing LeRobot, connecting Piper, creating `can0`, or downloading checkpoints:

```bash
set -a
source .env.example
set +a
bash scripts/record_piper_act.sh
bash scripts/train_act_autodl.sh
bash scripts/rollout_act_local.sh
```

Dry-run mode validates configuration shape and prints commands. It does not prove device discovery, CUDA capacity, checkpoint compatibility, camera ordering, network latency, collision clearance, or task success.

## Promotion to measured data

When hardware becomes available, copy `results/result_template.md` and set `Value origin` to `measured`. Record the repository commit, resolved configuration, sanitized logs, checkpoint identity, episode count, success count, and reviewer. Never overwrite the reference profile with an unreviewed measurement.
