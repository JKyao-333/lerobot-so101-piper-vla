# SmolVLA fine-tuning

Two workflows must remain distinct:

- SmolVLA LIBERO policy evaluation measures simulated benchmark behavior.
- SmolVLA Base + Piper LeRobot dataset fine-tuning produces a real-robot task policy.

The Piper wrapper maps `observation.images.front` and `observation.images.wrist` to the policy's `camera1` and `camera2` keys. The completed source experiment used batch size 4, 4 workers, 20,000 steps, and a 5,000-step save frequency. Base model, SmolVLM path, dataset, output, learning rate, device, offline mode, resume checkpoint, and LoRA settings remain environment-specific runtime inputs.

LeRobot 0.6.1 exposes PEFT/LoRA through `--peft.method_type` and `--peft.r`. Its verified SmolVLA config does not expose a quantized-training flag, so this repository rejects `QUANTIZATION_ENABLE=true` instead of forwarding an invented option. Run outputs, checkpoints, datasets, and caches are ignored by Git.
