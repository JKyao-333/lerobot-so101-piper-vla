# OpenVLA-LIBERO evaluation

This workflow evaluates OpenVLA in LIBERO's MuJoCo simulation only. It does not claim an OpenVLA Piper deployment.

The wrapper accepts `--suite spatial|object|goal|long`, a local checkpoint path or Hugging Face repository id, a wrapper log directory, and center-crop boolean. Execute mode verifies the OpenVLA and LIBERO roots, imports LIBERO/MuJoCo, requires headless EGL when no display exists, and stores the captured console log in a suite-specific timestamped directory. The manual profile maps the four suites to the corresponding `openvla/openvla-7b-finetuned-libero-*` ids.

No OpenVLA source checkout or commit was supplied for CLI inspection. The wrapper therefore sends only the four arguments present in the supplied manual: `--model_family`, `--pretrained_checkpoint`, `--task_suite_name`, and `--center_crop`. It does not invent an attention-backend or upstream output-directory flag. The wrapper's `--output-dir` controls only its captured console log; OpenVLA video and artifact locations depend on the installed revision and are not indexed by this repository.

Raw evaluation logs and rollout artifacts stay outside Git. A sanitized result can be added only after the installed revision's real outputs identify the suite, episode count, success count, and success rate. No such logs were included in the current public input set, so this repository publishes no metric.
