# DROID 公共数据集工程附录

DROID 在本项目中是独立的数据工程练习，不属于 SO-101/Piper 自采数据。作者基于官方 `droid_raw/1.0.1` 完成了受控候选发现、混合 success/failure 抽样、可恢复下载、空间上限、HDF5 结构检查和多视角视频检查。

## 已检查样本

公开的脱敏摘要记录了 10 个 episode（4 success、6 failure）、10 个 `trajectory.h5`、30 个 MP4、共 3,852 个 timestep。每个 HDF5 包含 73 个 dataset；视频为 H.264、1280×720、60 FPS。身份字段和原始文件不发布。精确、机器可读的边界见 [`droid_sample_manifest.yaml`](../configs/reference/droid_sample_manifest.yaml)。

## 下载器

[`build_droid_subset.py`](../scripts/build_droid_subset.py) 保留官方 GCS 目录结构，只选择 `trajectory.h5`、顶层 JSON 和非 stereo MP4，支持：

- success/failure、lab、日期和 episode 数限制；
- 固定 seed 抽样和已有列表排除；
- `gsutil cp -n` 断点恢复；
- 下载数量、总目录大小和剩余磁盘空间保护；
- 单线程或受限并发下载。

默认模式只列出候选，不下载；必须增加 `--execute-download` 才写入数据目录。例如：

```bash
python scripts/build_droid_subset.py \
  --target-episodes 10 \
  --max-gb 50 \
  --episode-list-output data/droid_candidates.txt

python scripts/build_droid_subset.py \
  --execute-download \
  --target-episodes 10 \
  --max-gb 50 \
  --output-root data/droid_raw_subset \
  --downloaded-list-output data/droid_downloaded.txt
```

仓库不提交上述列表、原始数据、视频或 metadata。使用者需自行核对 DROID 的许可证、访问条件和存储预算。

## 声明边界

标签为 `upstream_public_dataset`、`user_executed_dataset_engineering` 和 `locally_inspected`。不声称作者采集或拥有 DROID，也不声称在该样本上完成训练、获得任务成功率或代表整个 DROID 数据分布。
