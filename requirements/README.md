# Software environment sources

`robot-runtime.txt` pins the two source revisions that were available in the supplied project material:

- LeRobot commit `e40b58a8dfa9e7b86918c374791599d070518d11` (package version 0.6.1);
- `lerobot_robot_piper` commit `abf721d9e88ac822b18cb3413a75bb8cc0e3b34f` (package version 0.1.0).

The Piper adapter declares `python-can` and `piper_sdk` as dependencies. The supplied material did not establish an exact Piper SDK revision, so this repository does not invent a pin; after installation, record the resolved distribution version in the deployment record.

The target Ubuntu host must provide Python 3.10 or newer, `python3-venv`, Git, `ip` (iproute2), and `v4l2-ctl` (v4l-utils). System-package installation remains an administrator action because distro versions and privilege policy are host-specific; `scripts/check_robot_environment.sh` reports missing commands before hardware onboarding.

ACT and SmolVLA are provided by the pinned LeRobot source. OpenVLA and LIBERO remain a separate simulation-only environment because no verifiable source revisions were supplied. They are intentionally excluded from the Robot PC bootstrap rather than silently installing unpinned simulation code.

Run [`scripts/setup_robot_software.sh`](../scripts/setup_robot_software.sh) from the repository root. It previews commands by default and performs network/package installation only with `--execute`.
