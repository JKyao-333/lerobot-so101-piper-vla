# Reproduction status

The completed source experiment and validation of the current repository revision are tracked separately.

| Layer | Status | Meaning |
| --- | --- | --- |
| Source experiment robot operation | Completed | The SO-101/Piper hardware chain was operated |
| ACT recording and training | Completed | Run parameters came from completed experiment records |
| Dual-ACT long-horizon task | Completed | The task was run; this repository supplies the engineered orchestration |
| OpenVLA four suites | Completed | Spatial, Object, Goal, and Long were evaluated |
| SmolVLA Piper fine-tuning | Completed | Fine-tuning used recorded Piper robot data |
| SmolVLA synchronous rollout | Completed | Local synchronous rollout was run |
| SmolVLA asynchronous inference | Completed | Policy Server, SSH tunnel, and Robot Client were connected |
| Current revision configuration | CI Verified | Schema, semantics, and projections were checked without hardware |
| Current revision MockRobot | CI Verified | State-machine and safety-gate behavior were checked with mocks |
| Current revision hardware replay | Pending replay | This commit has not yet been replayed end-to-end on the target hardware |

`Pending replay` does not mean the project has never used hardware. It states only that the engineering refactor represented by the current commit still needs a new end-to-end hardware run. CI intentionally has no robot, CAN interface, camera, GPU model, or checkpoint; its purpose is software reproducibility and safe command construction.
