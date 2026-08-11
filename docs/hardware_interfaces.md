# Hardware Interfaces

本文只描述源实验与当前仓库明确使用的物理/软件模块，不扩展传感器、控制器或安全硬件清单。接口参数是部署前需要重新核对的配置，不代表当前 revision 已重新连接真机。

## 接口清单

| 模块 | 接口 | 工程作用 | 当前仓库边界 |
| --- | --- | --- | --- |
| SO-101 Leader | Serial | 提供人工示教与遥操作输入 | 串口路径由环境变量配置；CI 不枚举或连接设备 |
| Piper | SocketCAN `can0`，1 Mbps | 接收机器人控制动作并返回机器人状态 | 真正发送动作需要配置与命令行双重授权；软件限幅不替代物理停止 |
| Front / Wrist Camera | USB video | 提供固定全局视角与腕部近景视觉观测 | camera index、视角、分辨率、FPS 和观测键必须与采集时一致 |
| Robot PC | Ubuntu runtime host | 运行 LeRobot、相机采集、策略客户端、安全编排与 Piper 接口 | 是动作发送边界所在主机；网络侧 Policy Server 不直接控制 CAN |
| Policy Runtime | Python inference process | 加载 ACT/SmolVLA checkpoint 与 processors，生成候选动作 | 候选动作仍须经过动作过滤和显式执行门控；OpenVLA 只用于 LIBERO 仿真 |

## 数据与控制方向

```text
SO-101 Leader --Serial--> Teleoperation / Dataset Collection
Front + Wrist Camera --USB video--> Dataset Collection / Policy Runtime
Checkpoint + processors --> Python Policy Runtime --> action filter
action filter --> Robot Interface --> SocketCAN can0 --> Piper
Piper state -----------------------> Dataset Collection / Policy Runtime
```

Robot Interface 指本仓库适配层与上游 `lerobot_robot_piper` 的组合，不是一块额外硬件。Policy Runtime 也只是 Robot PC 或策略服务主机上的 Python 进程，不应被描述成独立控制器。

## 部署一致性要求

- SO-101 串口、CAN 接口名、bitrate 和相机 index 必须来自目标机器的实际发现结果。
- front/wrist 命名、图像尺寸、FPS、任务文本、状态键和动作维度必须贯穿采集、训练与部署。
- checkpoint 必须与其 policy 类型、preprocess 和 postprocess 成套加载，不能只复制权重文件后混用 processors。
- CI、dry-run 与 MockRobot 不连接上述硬件，只验证配置、命令、状态机和动作发送门控。

更完整的接线与接入顺序见 [hardware topology](hardware_topology.md)、[hardware onboarding](hardware_onboarding.md) 和 [safety](safety.md)。
