# ACT pipeline

The validated workflow is:

`SO-101 leader → Piper teleoperation → front/wrist observations → lerobot-record dataset → cloud lerobot-train ACT → pretrained_model transfer → local lerobot-rollout → Piper`.

All identity-bearing values are runtime inputs. Dataset quality guidance from the practical material is retained as engineering rules: record one task per dataset, keep cameras and initial conditions stable, reject failed/colliding trajectories, and verify a short recording before a full collection.

The trusted manual profile uses 50 demonstrations and a 20,000-step checkpoint as reference values. The ACT manuals do not pin batch size or save cadence across LeRobot versions, so those two settings remain version-controlled defaults rather than invented numbers. Reference values are configuration inputs, not measured convergence evidence. A real run should capture its resolved command, dependency versions, output path, selected checkpoint, and sanitized log in an experiment record.
