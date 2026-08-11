# 工程证据索引

| 证据 | 等级 | 支持的声明 | 不支持的声明 |
| --- | --- | --- | --- |
| [`measured_experiment_baseline.yaml`](../configs/reference/measured_experiment_baseline.yaml) | `experiment_recorded` / 用户确认 | 源实验参数与完成范围 | 当前 commit 真机回归、性能指标 |
| [9 份原创手册](manuals/README.md) | `experiment_recorded` | 作者的实验流程、命令与参数记录 | 上游算法原创性 |
| [`publication_assets.yaml`](../configs/reference/publication_assets.yaml) | `CONFIRMED` | 手册数量、页数、SHA-256、发布审查状态 | PDF 中每条命令在所有未来版本可用 |
| 单元测试与 dry-run | `CONFIRMED` | 配置语义、命令构造、Mock 状态机、安全门 | 机器人动作效果、GPU 训练结果 |
| 当前 revision 硬件 replay | `NOT_VERIFIED` | 暂无 | 不得由历史实验或 CI 推导 |
| [`droid_sample_manifest.yaml`](../configs/reference/droid_sample_manifest.yaml) | `locally_inspected` | 本地 10 episode 样本结构和数量摘要 | DROID 所有数据统计、采集所有权、模型效果 |

证据等级定义见 [reproduction status](reproduction_status.md)。运行 `python scripts/validate_publication_assets.py --json` 可复核公开手册哈希与 DROID 摘要内部一致性。
