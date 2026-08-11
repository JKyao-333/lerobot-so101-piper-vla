# Safety

This project is research/teaching software, not a safety-certified robot controller.

Before every powered run:

- Keep the physical emergency stop reachable and verify it independently.
- Clear people, hands, cables, glass, liquids, sharp objects, and unrelated equipment from the workspace.
- Keep a trained operator beside the stop control; do not run unattended.
- Validate both ACT skills separately at low speed before combining them.
- Make the first combined run a dry-run and then an empty-scene test.
- Match camera identity, position, orientation, resolution, and task text to data collection.
- Never oppose a torque-enabled robot by hand.
- Stop immediately on vibration, reversed direction, unexpected acceleration, communication loss, or approach to a limit.

Software range and delta limits cannot detect table collisions, stalls, pinches, human contact, or every sensor/CAN failure. The current asynchronous Robot Client has no additional client-side safety timeout, and the server observation-queue timeout is not a robot-stop guarantee. A failed link can also prevent a hold command from arriving. Physical stop and supervision remain mandatory.

With the pinned Piper adapter, `use_degrees=false` uses normalized joint positions (approximately `[-100, 100]`) and a normalized gripper range of `[0, 100]`; it does not use radians. The dual-ACT `[-95, 95]` bound is a conservative normalized action boundary from the course manual, not a physical joint-angle limit.

Any invalid action fails fast: the first dimension, numeric, finite-value, absolute-bound, or step-delta violation enters `ABORTED` and attempts a best-effort position hold. The hold prefers a complete measured current pose and uses the last safe command only when measurement is unavailable. That hold is not an emergency stop. It may fail when the control channel or upstream private interface is unavailable, and such failure is logged without replacing the original fault.

Partial connection, camera setup, dataset-feature construction, policy loading, or processor loading failures trigger best-effort cleanup. Cleanup errors are logged and must not replace the original initialization error.

All provided hardware commands default to preview or disabled action transmission. Dual-ACT execution requires both `allow_robot_execution=true` in the local config and `--execute-robot` on the command line. Enabling execution remains an explicit, local operator decision.
