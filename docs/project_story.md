# 项目工作全景

这个仓库记录的不是一次模型接口演示，而是一条从机器人设备到策略执行的完整实验链。作者先完成 SO-101 follower/leader 的 Linux 环境、串口识别、校准和遥操作，再完成独立 SO-101 ACT 与 SO-101 leader 控制 Piper 的示教数据采集；随后把数据上传至训练环境，完成 ACT/SmolVLA 训练、checkpoint 回传与本地 rollout，并把两个 ACT 技能组织为带人工交接和失败出口的长程任务。OpenVLA 在 LIBERO 中作为仿真评测旁路，DROID 则用于练习大规模上游数据集的受控抽样、断点续传、存储保护和结构检查。

公开仓库的工程化工作把上述实验整理为可配置脚本、来源清单、安全门控、Mock 状态机、环境检查器、测试、CI 和复刻文档。这样既保留实验事实，也使复刻者能够先在无硬件环境验证软件，再逐级接入设备。

## 能力链

```text
Hardware -> Linux -> Robot I/O -> Data Pipeline -> AI Policy -> Runtime -> Robot Deployment
```

- Hardware / Linux：机械臂、电机控制板、串口、USB 相机、SocketCAN 和权限配置。
- Robot I/O：SO-101 leader/follower 遥操作与 Piper adapter 接口。
- Data Pipeline：任务文本、机器人状态、双相机视频、LeRobot dataset、压缩与传输。
- AI Policy：ACT、OpenVLA、SmolVLA 的训练或评测入口与 checkpoint 管理。
- Runtime：同步 rollout、双策略状态机、异步 Policy Server/Robot Client。
- Deployment：默认预演、显式执行门、动作过滤、超时、人工确认和证据记录。

## 不声称的内容

本项目不声称原创 ACT、OpenVLA、SmolVLA、LeRobot 或 DROID，也不把 CI/Mock 结果当作当前 revision 的真机复测。原始数据、checkpoint、完整视频和私有日志不进入仓库；没有证据文件的成功率、loss、延迟与训练耗时不发布。
