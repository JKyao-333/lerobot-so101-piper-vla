# Hardware topology

- SO-101 leader: human teleoperation input over a parameterized serial device.
- Ubuntu robot computer: LeRobot process host, camera capture, safety wrapper, and SocketCAN endpoint.
- Piper: execution robot on `can0`, bitrate `1000000`, with gripper enabled and the project workflow using `use_degrees=false`.
- Front camera: fixed global scene view.
- Wrist camera: fixed near-end-effector view.
- GPU host: receives a private dataset for training or runs a policy server; it does not directly own the robot safety boundary.

Camera names, positions, orientation, resolution, FPS, action representation, and task text must remain consistent between collection and deployment.

