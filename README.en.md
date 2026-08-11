# SO-101 / Piper Robot-Learning Deployment Engineering

This repository turns a completed laboratory workflow into a reproducible, safety-gated engineering project. It covers SO-101 setup and teleoperation, standalone SO-101 ACT, SO-101-to-Piper ACT, dual-ACT long-horizon orchestration, OpenVLA evaluation in LIBERO, SmolVLA fine-tuning/deployment, and a bounded DROID data-engineering exercise.

The author's work spans hardware bring-up, Linux and device setup, teleoperation, dual-camera data collection, cloud training workflows, checkpoint transfer, local rollout, long-horizon task composition, troubleshooting, dataset inspection, and the nine original Chinese lab manuals published in [`docs/manuals`](docs/manuals/README.md). The project uses upstream LeRobot, ACT, OpenVLA, SmolVLA, LIBERO, the Piper adapter, and Piper SDK; it does not claim those models or frameworks as original inventions.

## Evidence boundary

- `experiment_recorded`: parameters transcribed from experiments completed by the author.
- `CONFIRMED`: repository behavior verified on the current revision by tests or static validation.
- `PARTIAL_CONFIRMED`: only a bounded part of a workflow was verified.
- `NOT_VERIFIED`: hardware-dependent behavior not replayed on the current revision.

The source experiments included physical robot operation, recording, training, evaluation, and rollout. The refactored repository revision is currently verified through configuration validation, dry-run command previews, MockRobot tests, and CI only. No success rate, loss curve, latency, or timing claim is published without a retained evidence artifact.

## Engineering scope

| Track | What is included | Current-revision boundary |
| --- | --- | --- |
| SO-101 foundation | Ubuntu setup, serial discovery, calibration/teleoperation guidance, local recording | scripts default to preview; hardware is `NOT_VERIFIED` |
| ACT | standalone SO-101 and Piper recording, training, checkpoint transfer, rollout | recorded parameters plus dry-run wrappers |
| Dual ACT | two isolated policies, human handoff, action filtering, fail-closed execution gate | MockRobot and unit-tested state machine |
| OpenVLA | LIBERO Spatial/Object/Goal/Long evaluation wrapper | simulation only, not Piper deployment |
| SmolVLA | Piper fine-tuning, synchronous and server/client deployment paths | no current-revision GPU or robot replay |
| DROID | controlled subset discovery/download, resume/storage protection, HDF5/video inspection | upstream dataset; no ownership or collection claim |

See the [project story](docs/project_story.md), [contribution matrix](docs/contribution_matrix.md), [evidence index](docs/evidence_index.md), and [credits/provenance](docs/credits_and_provenance.md).

## Quick start

Requirements: Ubuntu/Linux and Python 3.12 for the pinned LeRobot runtime.

```bash
git clone https://github.com/JKyao-333/lerobot-so101-piper-vla.git
cd lerobot-so101-piper-vla
bash scripts/setup_robot_software.sh
bash scripts/setup_robot_software.sh --execute
source .venv/bin/activate
make validate
make workflow-dry-run
cp .env.example .env
python scripts/environment_check.py --profile software --strict
```

Setup and workflow scripts never move a robot by default. Hardware commands require the documented explicit execute flag, local device configuration, physical stop capability, and an on-site operator. Start with [SO-101 setup](docs/so101_setup.md), [SO-101 ACT](docs/so101_act_pipeline.md), or the [Piper deployment checklist](docs/deployment_checklist.md).

## Licensing

Original code is MIT licensed. The author's manuals and original documentation/artwork are licensed under CC BY 4.0. Upstream projects and DROID retain their own licenses and terms; see [credits and provenance](docs/credits_and_provenance.md).
