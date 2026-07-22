# ACT pipeline

The validated workflow is:

`SO-101 leader → Piper teleoperation → front/wrist observations → lerobot-record dataset → cloud lerobot-train ACT → pretrained_model transfer → local lerobot-rollout → Piper`.

All identity-bearing values are runtime inputs. Dataset quality guidance from the practical material is retained as engineering rules: record one task per dataset, keep cameras and initial conditions stable, reject failed/colliding trajectories, and verify a short recording before a full collection.

Training steps, batch size, save frequency, hardware model, and checkpoint selection are deliberately unset in public examples unless a future sanitized log proves them. A local run should capture its resolved command, dependency versions, output path, and selected checkpoint in a private experiment record.

