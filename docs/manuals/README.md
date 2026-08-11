# 原创实验手册

本目录收录作者 JKyao-333 在完成对应实验后撰写的 9 份中文实操手册，采用 [CC BY 4.0](../LICENSE-DOCUMENTATION.md)。它们是源实验记录与复刻教程；仓库脚本和配置是在这些记录基础上的可测试工程投影。

| 手册 | 主题 |
| --- | --- |
| `LeRobot_SO101_从零搭建与遥操作实验手册.pdf` | Ubuntu、环境、端口、校准、遥操作和本地录制 |
| `SO101_ACT实验手册.pdf` | SO-101 数据采集、ACT 训练和本地 rollout |
| `SO101_Piper_ACT实验手册.pdf` | SO-101 leader 到 Piper 的 ACT 闭环 |
| `ACT长程任务实践说明.pdf` | 长程任务拆分原则 |
| `Piper双ACT长程任务实践手册.pdf` | 双 ACT 策略编排与真机流程 |
| `OpenVLA_LIBERO_可视化评测实验手册.pdf` | OpenVLA 四类 LIBERO 仿真评测 |
| `SmolVLA教学手册.pdf` | SmolVLA 训练与同步/异步部署 |
| `SmolVLA_LIBERO训练提升选做手册.pdf` | SmolVLA-LIBERO 选做训练 |
| `DROID数据集可视化实验手册.pdf` | DROID 子集与 HDF5/视频可视化 |

发布前已进行提取文本扫描和人工审查，未发现 token、密码、个人邮箱/电话或用户主目录。手册中保留的云端地址/端口均在原文明确标为示例，复刻时必须替换。文件页数和 SHA-256 由 [`publication_assets.yaml`](../../configs/reference/publication_assets.yaml) 固定，可运行：

```bash
python scripts/validate_publication_assets.py --json
```

手册反映写作时的上游工具和实验环境；上游 CLI 可能变化，请以本仓库锁定版本和 dry-run 输出为准。原始数据、模型权重、完整视频、设备标识和私有日志不在本目录发布。
