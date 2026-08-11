# ACT pipeline

The validated workflow is:

`SO-101 leader → Piper teleoperation → front/wrist observations → lerobot-record dataset → cloud lerobot-train ACT → pretrained_model transfer → local lerobot-rollout → Piper`.

All identity-bearing values are runtime inputs. Dataset quality guidance from the practical material is retained as engineering rules: record one task per dataset, keep cameras and initial conditions stable, reject failed/colliding trajectories, and verify a short recording before a full collection.

The measured experiment baseline records 50 demonstrations and a 20,000-step checkpoint from the completed source run. The supplied records do not pin ACT batch size or save cadence across LeRobot versions, so those two settings remain version-controlled defaults rather than reconstructed values. These run parameters establish configuration provenance but do not create missing convergence metrics. A current-commit replay should capture its resolved command, dependency versions, output path, checkpoint, and sanitized evidence in a separate result record.
