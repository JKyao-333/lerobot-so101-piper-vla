# Changelog

## Unreleased

- Reframe the repository around robot-learning data pipelines, inference runtime, staged deployment, and failure analysis.
- Add Dataset Pipeline, Inference Runtime, Robot Deployment, and Failure Analysis guides.
- Add Hardware Interfaces, Dual ACT Design, and Deployment Checklist guides.
- Present the complete SO-101 demonstration-to-Piper-execution learning loop in README.
- Classify generic failure cases as `Troubleshooting Example` unless an explicit source record exists.
- Add standardized ACT rollout, Dual ACT, deployment, and troubleshooting evidence templates.
- Add a read-only Python environment checker for dependencies, configs, checkpoints, cameras, and CAN.
- Add a dry-run-first Ubuntu Robot PC bootstrap with evidence-backed LeRobot and Piper-adapter source pins.
- Separate software checks from deployment presence checks and keep both distinct from hardware evidence.
- Add documentation contract tests for links, baseline values, architecture, hardware inventory,
  dual-ACT design, deployment phases, evidence templates, environment readiness, failure evidence
  labels, script entrypoints, and the OpenVLA simulation boundary.

## 0.1.0 - 2026-07-23

- Add parameterized ACT data collection, training, checkpoint transfer, and rollout wrappers.
- Add a hardware-independent dual-ACT state machine with manual handoff and action safety checks.
- Add OpenVLA-LIBERO four-suite evaluation and SmolVLA fine-tuning/deployment wrappers.
- Add reproducibility, safety, sanitization, tests, and CI documentation.
