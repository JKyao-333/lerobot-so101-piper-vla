# Architecture

The repository separates four responsibilities:

1. Upstream execution: LeRobot policies, processors, CLI tools, LIBERO environments, OpenVLA, and the Piper adapter remain external dependencies.
2. Workflow wrappers: shell scripts translate environment/CLI inputs into upstream commands and default to preview mode.
3. Orchestration: `robot_learning.dual_act` owns the public two-skill state machine and the lazy LeRobot/Piper bridge.
4. Safety and evidence: action filtering, watchdogs, log redaction, artifact checks, tests, and result templates prevent unsafe or unsupported publication claims.

The deep seam is `SkillRuntime`: orchestration sees a policy plus its own processors and metadata, while upstream model internals remain opaque. The robot seam is a small observation/send/stop protocol, which permits `MockRobot` tests without hardware.

No code here modifies ACT architecture, Transformer layers, vision backbones, losses, or training algorithms.

