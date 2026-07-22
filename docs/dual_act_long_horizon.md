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
- Hardware send is gated by `--execute-robot`; mock mode is the default.

The action filter clips verified finite values but rejects dimension and non-finite errors. It cannot validate scene geometry or collisions.

