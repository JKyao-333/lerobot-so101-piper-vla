# 独立 SO-101 ACT 实验链

SO-101 ACT 是独立于 Piper ACT 的第一阶段实验。实验记录使用 SO-101 follower/leader、front/side 双相机、50 条 episode、每条 30 秒、reset 15 秒和 30 FPS；训练流程选取 020000 checkpoint，再回到本地执行 rollout。

## 配置投影

- 录制模板：[`configs/act/so101_record.example.yaml`](../configs/act/so101_record.example.yaml)
- rollout 模板：[`configs/act/so101_rollout.example.yaml`](../configs/act/so101_rollout.example.yaml)
- 主机变量：`.env.example` 中的 `SO101_*`、`LEADER_*`、相机与任务字段
- 完整记录：[SO101_ACT 实验手册](manuals/SO101_ACT实验手册.pdf)

## 默认预演

```bash
set -a
source .env.example
set +a
bash scripts/teleoperate_so101.sh
bash scripts/record_so101_act.sh
bash scripts/train_act_autodl.sh
bash scripts/rollout_so101_act_local.sh
```

前三个 SO-101 设备脚本只有增加 `--execute-robot` 才会调用真实机器人 CLI。训练脚本的参数由数据路径和输出路径控制；运行前必须保证训练数据的 observation keys、相机名称和动作维度与部署一致。

## 证据边界

上述 50 episodes、30 FPS、30/15 秒和 020000 checkpoint 来自作者已完成的源实验，标记为 `experiment_recorded`。本仓库当前只验证参数投影、命令预演和文件契约，未重新接入硬件或加载 checkpoint，因此当前 revision 的 SO-101 真机结果仍为 `NOT_VERIFIED`。
