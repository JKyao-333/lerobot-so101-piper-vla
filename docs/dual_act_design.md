# Dual ACT Design

## 设计背景

长程机器人任务会把多个接触、抓取和放置阶段串在一起。前一阶段的小误差可能改变物体位置、机器人姿态或相机观测，随后继续执行会放大误差并把失败传播到后续阶段。本仓库没有修改 ACT 网络，而是把源实验中的长程任务拆成两个独立训练、独立加载、人工确认交接的技能。

```text
Skill A checkpoint + processors
              |
              v
INIT -> SKILL_A -> WAIT_CONFIRM -> SKILL_B -> DONE
                         |              ^
                         |              |
                         +-- operator --+

active stage / timeout / invalid action / rejection -> ABORTED

Skill B checkpoint + processors --------------------^
```

核心交接路径是 `Skill A -> WAIT_CONFIRM -> Skill B`。Skill A 结束不会自动触发 Skill B；现场操作员需要先检查物体位置、机器人姿态与工作区，再显式确认。拒绝、未知输入、非交互终端、超时或异常均失败关闭到 `ABORTED`。

## 运行时组成

| 组成 | 实现 | 目的 |
| --- | --- | --- |
| 两个 checkpoint | `skills.a.checkpoint`、`skills.b.checkpoint` | 将两个技能的模型身份与任务文本分开；默认禁止意外共享路径 |
| 两套 processors | 每个 `SkillRuntime` 各自绑定 preprocess 与 postprocess | 保持观测特征、设备处理和动作解码与对应 checkpoint 一致 |
| 状态机 | `INIT -> SKILL_A -> WAIT_CONFIRM -> SKILL_B -> DONE/ABORTED` | 让交接、timeout、完成和中止条件可测试、可审查 |
| policy reset | 任务开始时重置 A/B；确认交接时再次重置 B | 清空策略内部时序缓存，不访问 `_action_queue` 等私有实现 |
| 动作限制 | `ActionFilter` 统一检查动作维度与有限值，再应用绝对/单步边界 | 在唯一发送出口前约束候选动作 |
| 执行门控 | 配置 `allow_robot_execution=true` 且命令行 `--execute-robot` | 防止仅因进入 hardware 模式就自动发送动作 |

这里的 processors 不是本仓库自研模型组件；它们由对应 LeRobot checkpoint 的上游加载流程创建。`policy.reset()` 使用公开接口，状态机不修改 ACT 内部 action queue。

## 动作与停止边界

`ActionFilter` 对错误维度、非数值和 NaN/Inf 直接拒绝；对有限动作应用配置中的绝对范围和单步变化范围。示例配置的 7 维动作、关节 `[-95, 95]`、夹爪 `[0, 100]` 和 step delta 来自手册基线，表示保守的归一化控制边界，不是 Piper 硬件角度限位，也不是碰撞检测。

进入 `ABORTED` 或退出时，运行时会尝试通过控制通道保持当前位置。该操作是 best-effort position hold，不是物理急停；真实部署仍要求现场监护、空工作区和可立即使用的物理停止手段。

## 工程权衡

优势是将长程任务的失败传播限制在技能边界，允许人工在 Skill B 前检查现场条件，也能单独回归每个 checkpoint、processor 集与任务文本。代价是需要管理多模型、多套 processors、checkpoint 路径和更多状态转换；人工交接还引入等待、timeout 和操作一致性问题。

因此该设计适合可分解、需要人工监督的研究与教学任务，但不等价于自主长程规划，也不证明任务成功率提高。实现细节见 [dual ACT long-horizon orchestration](dual_act_long_horizon.md) 与 [`configs/dual_act/dual_act.example.yaml`](../configs/dual_act/dual_act.example.yaml)。
