# SO-101 从零搭建与遥操作

本章把完整手册中的基础阶段投影为公开仓库入口。目标是先完成设备发现、校准和遥操作，再进入数据采集；任何脚本都默认只打印命令。

## 软件基线

- Ubuntu 22.04 实验环境。
- Python 3.12；与本仓库锁定的 LeRobot 0.6.1 源码要求一致。
- `lerobot[core_scripts,hardware,feetech]`、ffmpeg、v4l2 工具。
- follower/leader 的真实串口、校准 ID 和双相机编号必须在目标主机重新确认。

```bash
bash scripts/setup_robot_software.sh
bash scripts/setup_robot_software.sh --execute
cp .env.example .env
python scripts/environment_check.py --profile software --strict
```

## 分级接入

1. 断电检查电源电压、极性、3-pin 线方向和活动范围。
2. 上电后使用 `lerobot-find-port` 和 `lerobot-find-cameras opencv` 识别设备。
3. 按上游工具分别校准 follower 和 leader；校准 ID 必须与运行命令一致。
4. 先预演：`bash scripts/teleoperate_so101.sh`。
5. 现场操作员确认急停/断电可达、人员和线缆离开活动范围后，才运行 `bash scripts/teleoperate_so101.sh --execute-robot`。
6. follower 方向错误、抖动、撞限位趋势或通信异常时立即停止，不进入录制。

`chmod 666` 只适合临时实验排障；长期环境优先通过 udev 规则或用户组配置最小权限。完整图文步骤见 [原创手册](manuals/LeRobot_SO101_从零搭建与遥操作实验手册.pdf)。当前 revision 未在用户硬件上重放，状态为 `NOT_VERIFIED`。
