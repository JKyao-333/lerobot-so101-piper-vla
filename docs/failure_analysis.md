# Failure Analysis

故障分析围绕机器人学习闭环定位问题：环境与设备、数据、训练、checkpoint、推理运行时、通信、安全出口和证据记录。目标是可重复地缩小故障范围，不通过虚构指标或扩大动作边界掩盖问题。

## 处理原则

1. 先停止动作并确保物理停止手段可用。
2. 保存原始异常、时间、阶段和脱敏日志；清理错误不能覆盖原始错误。
3. 从最早失败的层级排查，不把训练问题直接归因于机器人硬件。
4. 每次只改变一个变量，并重新从对应的低 Level 验证。
5. dry-run/Mock/CI 只能证明软件路径，不证明当前硬件或性能。

## 证据分类

源手册与补充资料确认了实验链路、参数和部署方式，但当前公开仓库没有为下列每种故障提供逐项对应的原始故障日志、时间戳与处理记录。因此，下表全部属于 **Troubleshooting Example**（通用排障案例），用于指导诊断，不表示这些现象都在源实验中实际发生过。

只有带 repository commit、日期、原始异常、脱敏 evidence path 和处理结论的新记录，才可以在后续 revision 中升级为已复核的实验故障事实。

## Troubleshooting Examples（通用排障案例）

| 证据类型 | 阶段 | 示例现象 | 优先检查 | 安全响应 |
| --- | --- | --- | --- | --- |
| Troubleshooting Example | 环境 | 命令缺失、版本不符 | `check_robot_environment.sh`、上游版本、Python 环境 | 停在 Level 0/1，不连接硬件 |
| Troubleshooting Example | SO-101 | leader port 不存在/无权限 | 端口映射、权限、占用进程 | 不启动采集或 teleop |
| Troubleshooting Example | CAN | `can0` 不存在、bus-off、无反馈 | 实际接口名、bitrate、USB-CAN、线缆、电源 | 不反复盲目重建接口；断开动作执行 |
| Troubleshooting Example | 相机 | 打不开、对调、掉帧、视野变化 | 占用进程、index、front/wrist、分辨率/FPS | 停止 rollout，恢复数据采集视角 |
| Troubleshooting Example | 数据集 | episode/帧/键不一致 | 任务文本、FPS、reset、图像键、动作维度 | 隔离问题数据，不进入训练 |
| Troubleshooting Example | 训练 | OOM、路径错误、无 checkpoint | dataset root、device、batch、输出目录、依赖 | 调整环境参数并保留失败配置；不声称收敛 |
| Troubleshooting Example | Checkpoint | feature/processors 不匹配 | 相机键、action names、policy 类型、pre/post processors | 保持执行关闭，回到单技能加载验证 |
| Troubleshooting Example | 动作过滤 | malformed action 或持续触发 clipping | policy 输出、动作单位、previous action、limits | malformed action 立即 `ABORTED`；持续 clipping 先停止并调查 |
| Troubleshooting Example | 双 ACT | Skill B 未开始或误交接 | 状态机阶段、人工输入、task/checkpoint 区分 | n/no/q/未知输入均中止，重新检查交接 |
| Troubleshooting Example | Hold | 无法保持当前位置 | 控制通道、当前测量、last safe command、pinned `_iface` | 记录失败并使用物理停止机制 |
| Troubleshooting Example | 异步推理 | queue exhaustion、陈旧动作 | tunnel、server、FPS、chunk、服务端日志 | 停止 Robot Client；不把 server timeout 当停止保证 |
| Troubleshooting Example | LIBERO | EGL/MuJoCo import 失败 | `MUJOCO_GL=egl`、驱动、LIBERO/OpenVLA revision | 保持为仿真问题，不关联 Piper 真机 |
| Troubleshooting Example | 仓库验证 | secret/大文件/配置扫描失败 | 报告的具体文件与未脱敏路径 | 修复证据和配置，不跳过检查 |

## 分层定位流程

```text
仓库/配置失败?
  yes -> Level 0 修复
  no  -> 设备发现失败?
           yes -> 串口/CAN/camera/权限
           no  -> 数据或 checkpoint 契约失败?
                    yes -> task/camera/action/processors
                    no  -> 推理输出非法?
                             yes -> policy/units/filter
                             no  -> 发送或通信失败?
                                      yes -> CAN/local runtime/tunnel
                                      no  -> 场景行为异常，停止并检查数据分布与任务条件
```

## 已有自动化覆盖

- 配置字段、路径展开、频率、checkpoint 和 provenance 语义。
- 动作维度、非数值、NaN/Inf、绝对范围和 step delta。
- 双 ACT 状态转换、timeout、handoff 拒绝和 Mock 完成路径。
- 部分连接失败清理、disconnect 幂等、测量姿态 hold 和 fallback。
- shell wrapper dry-run、OpenVLA 参数边界、异步 timeout 配置一致性。
- secret scan、大文件/权重/视频检查和 `git diff --check`。

这些测试不覆盖真实 CAN 时序、相机驱动稳定性、机械碰撞、实际 hold 效果、GPU 性能、网络抖动或任务成功率。

## 故障记录最小字段

- repository commit 与 dirty 状态
- 日期、运行阶段和最后安全状态
- resolved config 与命令（脱敏）
- 数据集/checkpoint 标识
- 上游版本和运行环境摘要
- 原始异常与清理异常
- 是否发送过动作、是否使用物理停止
- evidence path、复现步骤、处理人和结论

使用 [troubleshooting record template](../results/troubleshooting_record_template.md) 保存诊断案例；其他实验记录入口见 [results](../results/README.md)。没有 evidence path、evaluation date、episodes/tasks 和 source record 时，不发布成功率、loss、延迟或耗时。
