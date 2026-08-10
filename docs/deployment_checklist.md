# Deployment Checklist

此清单用于把已通过 CI/Mock 的软件 revision 分级接入目标环境。它不授权无人监护运行，也不把 dry-run、MockRobot 或 CI 结果视为真机验证。

## 部署前（Pre-deployment）

- [ ] 记录 repository commit、dirty 状态、目标任务和操作人员。
- [ ] 在 Ubuntu Robot PC 创建隔离 Python 环境，并按 [upstream versions](upstream_versions.md) 安装匹配的 LeRobot、Piper adapter 与依赖。
- [ ] 运行 `python scripts/validate_experiment_baseline.py --json`、`make validate` 和 `make workflow-dry-run`。
- [ ] 检查 ACT/SmolVLA checkpoint 路径存在且类型正确；双 ACT 的 A/B checkpoint 与 task 对应，未意外共享。
- [ ] 确认每个 checkpoint 使用自己的 preprocess/postprocess；相机键、机器人状态键、动作名、维度和单位与训练一致。
- [ ] 在保持设备断电和动作发送关闭的准备阶段，核对急停/物理停止方案、工作区、线缆和人员职责；随后按现场规程分阶段上电。
- [ ] 发现并记录 SO-101 serial、front/wrist USB camera 与 Piper CAN 实际接口，不复制其他机器的设备路径。
- [ ] 检查 front/wrist 相机未对调，视角、方向、分辨率和 FPS 与采集配置一致。
- [ ] 检查 SocketCAN 接口名、1 Mbps bitrate、终端、电源和反馈状态；CAN 未健康时不得启用 rollout。
- [ ] `.env`、主机地址、用户目录和凭据只保存在本地，不提交到仓库或结果日志。

## 部署中（During deployment）

- [ ] 先运行 wrapper 默认 Dry Run，审查展开后的命令、路径、任务文本、设备和安全参数。
- [ ] 使用 MockRobot 跑通单技能和双技能状态转换，包括 `WAIT_CONFIRM`、拒绝、timeout 与 `ABORTED`。
- [ ] hardware 连接验证阶段保持 `--execute-robot` 关闭，先检查观测键、动作维度和反馈。
- [ ] 单独加载每个 checkpoint 与 processors，调用公开 `policy.reset()`，不要从双技能组合任务直接开始。
- [ ] 审查 `ActionFilter` 的 action dimension、absolute bounds 和 max step delta；不得为绕过错误而扩大边界。
- [ ] 只有配置 `allow_robot_execution=true` 与命令行 `--execute-robot` 同时明确授权时才允许动作发送。
- [ ] 首次动作验证采用空工作区、低速、短时、单技能和现场监护，物理停止手段始终可达。
- [ ] 双 ACT 在 Skill A 后停留于 `WAIT_CONFIRM`，人工检查物体、姿态和工作区后才能进入 Skill B。
- [ ] 出现相机中断、CAN 异常、陈旧观测、非法动作、持续 clipping、timeout 或未知状态时立即中止，不自动重试真机动作。

## 部署后（Post-deployment）

- [ ] 确认最终状态为预期的 `DONE` 或已安全处理的 `ABORTED`，不存在仍在运行的客户端、策略服务或动作进程。
- [ ] 保存脱敏日志、resolved config、checkpoint 标识、任务、时间、动作授权状态和 evidence path。
- [ ] 记录 hold/stop 是否成功；best-effort hold 失败时保留原始异常并执行现场物理停止流程。
- [ ] 核对相机、CAN、机器人反馈和网络客户端均已按现场规程退出，再执行断电/撤场。
- [ ] 将新数据或结果与原始数据分开，问题 episode 不直接进入下一轮训练。
- [ ] 若部署失败，回滚到已知可工作的 checkpoint、processor 集与配置，先恢复 Dry Run/Mock/单技能验证；不要用扩大限幅或跳过检查替代回滚。
- [ ] 只有 evidence path、日期、episodes/tasks 和 source record 完整时才发布结果；不补写未测成功率、loss、延迟或耗时。

接口清单见 [hardware interfaces](hardware_interfaces.md)，分级接入见 [robot deployment](robot_deployment.md)，异常定位见 [failure analysis](failure_analysis.md)，物理边界见 [safety](safety.md)。
