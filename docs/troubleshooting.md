# Troubleshooting

- CAN interface missing: inspect USB-CAN driver/cabling and the actual interface name; do not blindly recreate `can0`.
- Piper does not move: check power, CAN state/bitrate, adapter installation, and the explicit execution flag.
- Leader unavailable: re-run the upstream port finder and verify permissions without publishing the device serial.
- Camera open failure: release other processes and verify front/wrist mapping; an image appearing is not proof that cameras are correctly assigned.
- Policy feature mismatch: compare camera keys, image shapes, action dimension, `use_degrees`, and checkpoint processors.
- Unstable rollout: stop first; inspect data quality, task text, camera placement, action units, and checkpoint identity. Do not increase safety limits as a first response.
- LIBERO EGL failure: confirm driver/EGL visibility and `MUJOCO_GL=egl` before model debugging.
- Async queue exhaustion: stop the robot client; inspect inference latency, tunnel stability, FPS, chunk size, and server logs.

