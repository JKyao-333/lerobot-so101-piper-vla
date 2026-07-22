# OpenVLA-LIBERO evaluation

This workflow evaluates OpenVLA in LIBERO's MuJoCo simulation only. It does not claim an OpenVLA Piper deployment.

The wrapper accepts `--suite spatial|object|goal|long`, a checkpoint, output directory, and center-crop boolean. It verifies the OpenVLA and LIBERO roots, imports LIBERO/MuJoCo, requires headless EGL when no display exists, and creates a suite-specific timestamped run directory.

Raw evaluation logs and rollout videos stay outside Git. A sanitized result can be added only after the log identifies the suite, episode count, success count, and success rate. No such logs were included in the current public input set, so this repository publishes no metric.

If FlashAttention cannot be installed, set `ATTENTION_BACKEND=sdpa`. The wrapper records the backend in the private run log; compatibility remains the operator's responsibility.

