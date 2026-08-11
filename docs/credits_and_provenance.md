# Credits, provenance and licensing

## 原创范围

作者 JKyao-333 完成了本项目所记录的实验工作并撰写 9 份中文实操手册。本仓库原创的编排、安全、配置、测试和脚本封装采用 [MIT License](../LICENSE)；原创手册及原创文档/图稿采用 [CC BY 4.0](LICENSE-DOCUMENTATION.md)。引用时建议注明作者、仓库链接和对应文件名。

仓库的工程化整理包含在作者指令和审查下完成的辅助性协作。该说明用于透明呈现生产过程，不改变作者对实验、资料选择和公开发布的责任，也不把上游工作归为作者原创。

## 上游范围

LeRobot、ACT、OpenVLA、LIBERO、SmolVLA、`lerobot_robot_piper`、Piper SDK 和 DROID 均为上游项目或数据集，保留各自许可证、引用要求和商标。仓库只提供版本指针、参数化调用和复刻说明，不重新分发它们的完整源码、原始数据或权重。精确版本和链接见 [references](references.md) 与 [upstream versions](upstream_versions.md)。

## 数据边界

DROID 样本来自公共上游数据集。作者完成的是选择性下载、恢复与存储保护、HDF5/视频检查；不声称采集、拥有 DROID 或在该样本上完成模型训练。公开摘要排除了 building、robot serial、scene、user、user id 和 UUID 等身份字段。
