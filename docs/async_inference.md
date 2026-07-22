# Synchronous and asynchronous inference

Synchronous rollout keeps the policy, observation processing, safety gate, and Piper execution on the robot computer. It avoids a network dependency but requires sufficient local compute.

Asynchronous inference uses three separately supervised processes:

1. A loopback-only cloud Policy Server.
2. An SSH local port forward.
3. A local Robot Client that owns cameras and Piper.

In the verified LeRobot 0.6.1 protocol, the Policy Server is an empty service at startup. The Robot Client handshake supplies policy type, checkpoint path, and policy device. Server configuration exposes host, port, FPS, inference latency, and observation-queue timeout; it does not expose a batch-size field. The wrappers preserve that real API instead of inventing unsupported arguments.

The robot client script defaults to preview. Tunnel loss, server timeout, queue exhaustion, stale observations, or malformed actions must stop transmission and require operator intervention. SSH transport is not a safety-rated real-time fieldbus.

