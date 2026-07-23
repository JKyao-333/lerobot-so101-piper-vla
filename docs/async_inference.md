# Synchronous and asynchronous inference

Synchronous rollout keeps the policy, observation processing, safety gate, and Piper execution on the robot computer. It avoids a network dependency but requires sufficient local compute.

Asynchronous inference uses three separately supervised processes:

1. A loopback-only cloud Policy Server.
2. An SSH local port forward.
3. A local Robot Client that owns cameras and Piper.

In the inspected LeRobot 0.6.1 commit `e40b58a8`, the Policy Server is an empty service at startup. The Robot Client handshake supplies policy type, checkpoint path, and policy device. Server configuration exposes host, port, FPS, inference latency, and observation-queue timeout; it does not expose a batch-size field. `RobotClientConfig` also has no request or safety timeout field, so the wrapper does not emit one.

The robot client script defaults to preview. The Policy Server's `obs_queue_timeout` controls how long the server waits for an observation; it is not a robot-client stop guarantee. The current wrapper adds no client-side timeout protection. Tunnel loss, server failure, queue exhaustion, stale observations, or malformed actions require direct operator intervention. SSH transport is not a safety-rated real-time fieldbus.

The manual reference profile uses `/dev/video6` and `/dev/video5` at 640x480 and 10 FPS, a 15 Hz control loop, 50 actions per chunk, a 0.5 refill threshold, and `weighted_average`. Fifty actions at 15 Hz nominally cover 3.333 seconds. Device paths remain host-specific even when the other values are representative.
