# Dual ACT long-horizon orchestration

The project decomposes a long table-top task into two independently trained ACT skills. It does not implement a new ACT network or autonomous planner.

```text
INIT → SKILL_A → WAIT_CONFIRM → SKILL_B → DONE
  └──────────── any active state ───────────→ ABORTED
```

Rules:

- Both policies reset at task start; skill B resets again immediately before handoff.
- Skill A completion never starts skill B automatically.
- An interactive operator must inspect object placement and robot pose, then confirm.
- A non-interactive terminal, rejection, stage timeout, total timeout, invalid action, Ctrl+C, or exception aborts.
- Each skill keeps the preprocess/postprocess files from its own checkpoint.
- The bridge calls public `policy.reset()` and never changes `_action_queue`.
- Hardware send requires both `allow_robot_execution=true` in the config and `--execute-robot`; mock mode can never send real actions.

With the pinned Piper adapter, `use_degrees=false` represents joints in an approximately `[-100, 100]` normalized range and the gripper in `[0, 100]`; it does not mean radians. The configured `[-95, 95]` joint boundary is a conservative normalized action boundary from the course manual, not a hardware joint-angle limit.

The action filter clips finite values to configured absolute and step-delta limits, while dimension, non-numeric, and NaN/Inf inputs are rejected. The first invalid action immediately enters `ABORTED`; errors are not accumulated or ignored. The exit path attempts `hold_current_pose_best_effort()` even when a camera is offline. This is a position-hold attempt through the robot control channel, not a physical emergency stop; failures are logged and the original abort reason is preserved.

Because the pinned public Piper adapter couples `is_connected` to camera health, this hold path uses its private `_iface` only for `lerobot_robot_piper` commit `abf721d9e88ac822b18cb3413a75bb8cc0e3b34f`. Access is isolated in `_pinned_piper_control_interface()`, guarded with `getattr()`, and treated as unavailable on any mismatch. No other module accesses `_iface`, and upgrading the adapter requires revalidating this compatibility shim.
