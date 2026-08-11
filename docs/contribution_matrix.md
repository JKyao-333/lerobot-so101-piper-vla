# 个人贡献与上游边界

| 模块 | 作者完成的工作 | 复用的上游能力 | 公开证据 |
| --- | --- | --- | --- |
| SO-101 基础 | 环境搭建、端口识别、权限、校准、遥操作、本地录制、手册 | LeRobot SO-101/Feetech 支持 | 原创手册、配置、默认预演脚本 |
| SO-101 ACT | 双相机示教、50 episodes、30 FPS、训练与 020000 checkpoint rollout 流程 | LeRobot ACT policy/CLI | 基线、SO-101 wrappers、手册 |
| Piper ACT | SO-101 leader 到 Piper 的数据采集、15 FPS、训练、checkpoint 回传与本地 rollout | LeRobot ACT、Piper adapter/SDK | wrappers、配置、测试、手册 |
| 双 ACT | 长程任务拆分、两 checkpoint、人工交接、安全状态机和故障退出 | ACT policy 推理与 adapter | 原创编排代码、Mock 测试、手册 |
| OpenVLA | 四套 LIBERO 评测流程整理与执行记录 | OpenVLA、LIBERO、MuJoCo | 仿真 wrapper、配置、手册 |
| SmolVLA | Piper 数据微调、同步和异步部署链路整理与执行记录 | SmolVLA/LeRobot runtime | wrappers、配置、手册 |
| DROID | 受控抽样、下载恢复、磁盘保护、HDF5/视频检查 | DROID 公共数据与 GCS | 下载脚本、脱敏样本摘要、手册 |
| 仓库工程化 | 配置投影、环境检查、安全门控、测试、CI、公开脱敏与文档 | GitHub Actions 等通用工具 | 当前仓库源码与 CI |

仓库工程化整理是在作者确认范围和证据边界下完成的辅助性协作；实验设计、实验执行、原始资料和最终公开责任属于作者。具体上游版本见 [upstream versions](upstream_versions.md)。
