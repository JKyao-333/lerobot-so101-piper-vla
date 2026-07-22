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

Software range and delta limits cannot detect table collisions, stalls, pinches, human contact, or every sensor/CAN failure. Network timeout must stop new actions, but a failed link can also prevent a hold command from arriving. Physical stop and supervision remain mandatory.

All provided hardware commands default to preview or disabled action transmission. Enabling execution is an explicit, local operator decision.

