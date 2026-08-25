# Phase 2A-RL1 当前进度报告

更新时间：2026-08-25 10:52 (CST)

## 总体状态

```text
Norman pilot:                COMPLETE_AND_FROZEN（不重算）
Replogle Phase 2A:           CONDITIONAL_GO_GEARS_FILTERED
BNS:                         UNVERIFIED（本阶段不变）
RPE1 bounded smoke:          PASS（executable chain 证据，非性能）
R-L1-K562 full run:          COMPLETED_GEARS（训练完成；导出阶段 ctrl_adata fallback 后已 recovery 完成）
R-L1-RPE1 full run:          RUNNING（foreground full run；Epoch 5/20 已开始）
Norman/Replogle comparison:  PENDING（等待两个 full run）
Cross-context gate:          PENDING
```

## 接手记录

2026-08-24 20:14 CST 已接手当前任务。现场核对结果：

- K562 full run 仍在运行：PID `6542`，运行目录 `results/replogle/gears/rl1_k562_20260824T074041Z/`。
- watcher 正常写入 `logs/rl1_watch.log`，最新记录为 Epoch 9 Step 3151。
- 发现两个 `run_rl1_sequencer.sh` 实例同时等待 K562 完成；已终止旧实例 PID `4889`，保留 PID `6546`，避免 K562 完成后重复启动 RPE1。
- 已新增 postprocess 脚本：`scripts/run_rl1_postprocess_when_ready.sh`。当前 Codex 工具会在命令结束后回收新启动的后台 postprocess watcher，因此该 watcher 未保持常驻；K562/RPE1 两个 RL1 full run 都完成后，需要在持久终端或下一轮 Codex 中运行它，或直接运行 `PYTHONPATH=. python3 scripts/build_gears_rl1_analysis.py` 生成下游表和图。
- GEARS 训练进程未被改动；其他项目的 ContextKO 训练进程也未被干预。

## 已完成

1. **状态审计与冻结确认**
   - 读取全部状态文件；确认 Norman 冻结于 `d10d282`，premodel gate 于 `032c4a5`。
   - 冻结 R-L1 split 可复现性验证：`scripts/verify_replogle_rl1_split.py`
     - R-L1-K562 hash `e9fcaf7afdb972e4` ✓ 复现
     - R-L1-RPE1 hash `288d45dbeb512ce5` ✓ 复现
     - 输出 `results/replogle/rl1_split_reproducibility.csv`（PASS）

2. **STEP 1 — RPE1 bounded smoke：PASS**
   - 成功运行目录 `results/replogle/gears/gears_replogle_rpe1_smoke_20260823T072300Z/`
   - 全链条验证：load → split → graph → model init → train(1 batch, loss 0.7931) → predict → evaluate → save outputs
   - 1,177 s（GO graph 构建一次性开销）；seed=1；performance_eligible=false
   - 报告：`reports/REPLOGLE_RPE1_SMOKE_REPORT.md`
   - 一次失败尝试保留为 provenance（`..._20260823T072149Z/`，KeyError: AC118549.1+ctrl）

3. **STEP 2 — RL1 full-run 配置冻结**
   - `configs/replogle/gears_rl1_k562_seed1.yaml`、`configs/replogle/gears_rl1_rpe1_seed1.yaml`
   - 与 Norman pilot 一致：20 epochs / seed 1 / batch 16 / Adam 1e-3, wd 5e-4 / hidden 64 / essential perturbation graph
   - 偏差记录：`reports/PHASE2A_RL1_CONFIG_DEVIATIONS.md`
     - split-dict 在 GEARS vocabulary 内重建（同 Norman 惯例）
     - bootstrap 200 → 2000 resamples（本阶段锁定值）
     - 双 metric space：`gears_raw`（Norman 可比）+ `audit_delta`（baseline/probe 可比）
     - GO graph 官方式 top-k=20/target 修剪（见下）

4. **Full-run 执行链修复（三项 engineering fix，均记录 CHANGELOG）**
   - split-dict vocabulary mismatch（KeyError）→ 从 GEARS-filtered obs 重建
   - co-expression CSV 路径解析（OSError）→ PertData root 改为 dataset 父目录
   - GO graph 密度爆炸（12.1M edges vs Norman 134k，~90x 慢 + swap 风暴）→ 官方式 per-target top-k=20 修剪后 ~207k edges，恢复 Norman 同量级速度（0.16–0.25 s/step）

5. **基础设施**
   - `scripts/run_gears_replogle_rl1.py`：正式 full-run runner（官方 train loop 不改动；telemetry 捕获到 `training_log.csv`；双 metric space；perturbation-level bootstrap 95% CI 2000 resamples；严格 metadata 含 filtered_data/BNS/prior_hash/split_hash/git_commit/performance_eligible）
   - `scripts/build_gears_rl1_analysis.py`：RL1 summary 表、Norman 对照表、Metric Divergence Profile、GEARS vs probes 表、两张主图（pdf/svg/png）
   - watcher + sequencer：训练进度监控日志 `logs/rl1_watch.log`；K562 完成后自动启动 RPE1（`logs/rl1_sequencer.log`）

## 当前运行状态

| 项目 | 值 |
|---|---|
| 运行目录 | `results/replogle/gears/rl1_rpe1_20260825T000548Z/` |
| 数据集 | Replogle_RPE1_GEARS_filtered（filtered essential-screen data） |
| Split | R-L1-RPE1（frozen hash 已验证） |
| 进度 | Epoch 5/20（10:52 raw telemetry 已进入 Step 101） |
| 已完成验证 | Epoch 1 Validation Overall MSE 0.0227 / Top 20 DE MSE 0.1604；Epoch 2 0.0166 / 0.1275；Epoch 3 0.0186 / 0.1399；Epoch 4 0.0167 / 0.1275 |
| 资源 | foreground Python PID `74735`，约 200-270% CPU；训练阶段 RSS 约 2-8 GB 波动 |
| 预计 RPE1 完成 | 2026-08-25 晚间至夜间（前 4 轮约 35-45 分钟/epoch，完整 20 epoch 约 12-15 小时级） |

### K562 full-run 完成记录

- 运行目录：`results/replogle/gears/rl1_k562_20260824T074041Z/`
- 训练状态：20/20 epochs 完成；GEARS testing 完成。
- 原始 runner 在导出阶段触发 `AttributeError: 'NoneType' object has no attribute 'X'`，原因是 `pert_data.ctrl_adata` 为空。
- 已修复 `scripts/run_gears_replogle_rl1.py` 的 control fallback，并用 `scripts/recover_gears_replogle_rl1_export.py` 从已训练模型恢复导出，不重训。
- metadata：`status=COMPLETED`，`run_status=COMPLETED_GEARS`，`eval_predicted_perturbations=216`，`eval_truth_perturbations=216`，`n_ctrl_cells_audit=10691`。
- K562 summary：
  - `gears_raw`: Pearson 0.9851，top1 0.0139，top5 0.0417，MRR 0.0445，UER50 0，sign_flip 0。
  - `audit_delta`: Pearson 0.2840，top1 0.0139，top5 0.0556，MRR 0.0497，UER50 0.1580，sign_flip 0.2691。

### 接手后新增记录

- 2026-08-24 20:14 CST 接手：确认 K562 full run PID `6542`、watcher PID `6545`、sequencer PID `6546` 正常；发现并终止旧重复 sequencer PID `4889`，避免 K562 完成后重复启动 RPE1。
- 2026-08-24 21:22 CST：K562 进入 Epoch 11/20。
- 2026-08-24 22:15 CST：raw telemetry 确认进入 Epoch 12/20，约 Step 3051；watch log 采样略滞后但训练进程健康。
- 2026-08-24 22:20 CST：新增 `scripts/write_phase2a_rl1_reports.py`，并将 `scripts/run_rl1_postprocess_when_ready.sh` 扩展为在两 context 完成后依次生成表/图、`PHASE2A_RL1_FULL_REPORT.md` 和 `PHASE2A_CROSS_CONTEXT_GATE.md`。
- 2026-08-25 05:52 CST：K562 training/testing 已完成，但原始 run 在导出阶段因 `ctrl_adata=None` fallback 缺失失败；sequencer 因此未自动启动 RPE1。
- 2026-08-25 07:40 CST：新增并运行 `scripts/recover_gears_replogle_rl1_export.py`，K562 导出恢复完成，metadata 显式标记 `COMPLETED_GEARS`。
- 2026-08-25 08:05 CST：手动以前台方式启动 RPE1 full run，运行目录 `results/replogle/gears/rl1_rpe1_20260825T000548Z/`。
- 2026-08-25 09:03 CST：RPE1 Epoch 1 完成并通过 validation，Epoch 2 已开始；当前无需用户介入。
- 2026-08-25 10:52 CST：RPE1 Epoch 4 完成并通过 validation，Epoch 5 已开始；约完成 25% 训练轮次。

### 中断事件记录（已处置）

- 2026-08-23 22:33 机器重启（内存压力+并发任务导致），第一次 K562 run 于 epoch 7 被杀。
  - 该次运行已显式标记 `FAILED_GEARS_INTERRUPTED_SYSTEM_REBOOT`（provenance，不可误认为完成结果）
  - pyg cache / GO csv / co-expression csv 均保留，重跑无需重建
  - 2026-08-24 15:40 重新启动，当前 run 即为重启后的干净重跑

## 待办（按序）

1. 等 RPE1 full run 完成 → 校验 metadata/metrics 输出
2. 如 RPE1 在导出阶段遇到已知 post-train 问题，使用 `scripts/recover_gears_replogle_rl1_export.py --dataset rpe1 --run-dir <run_dir>` 从已训练模型恢复导出，不重训
3. 运行 `build_gears_rl1_analysis.py`：
   - `results/replogle/gears_rl1_summary.csv`（STEP 20 schema）
   - `results/tables/norman_replogle_rl1_comparison.csv`（STEP 21）
   - `results/tables/metric_divergence_profile.csv`（STEP 23 standardized rank difference）
   - `results/tables/replogle_gears_vs_probes.csv`（STEP 28 FP 对比）
   - `figures/main/norman_replogle_metric_divergence.{pdf,svg,png}`（主图1）
   - `figures/main/replogle_gears_vs_probes.{pdf,svg,png}`（主图2）
4. 统计比较（STEP 31）：within-Replogle K562 vs RPE1（bootstrap CI 重叠）；Norman vs Replogle 描述性对照（不做 pooled cell-level test）
5. 撰写 `reports/PHASE2A_RL1_FULL_REPORT.md`（回答 Q1–Q8）
6. 撰写 `reports/PHASE2A_CROSS_CONTEXT_GATE.md`（GO_RL4 / CONDITIONAL_GO_RL4 / HOLD_RL4；如信号高度一致附 MANUSCRIPT_SIGNAL 判断）
7. 更新 `analysis_lock.yaml`（phase2a_rl1 块）、`PROJECT_STATUS.md`、`NEXT_ACTIONS.md`、`CHANGELOG.md`
8. 最终 git checkpoint：`Complete Replogle RL1 external replication audit`

## 不变约束（HARD RULES，持续生效）

- 所有 Replogle 输出标注 **GEARS-compatible filtered essential-screen data**，不得称 full/complete Replogle dataset
- BNS 保持 **UNVERIFIED**；bns_role = sensitivity_only；batch/library/gemgroup/run/SRA run 一律不解释为 biological replicate
- UER null 来源 = per-perturbation median |audit delta|，`uer_null_status = sensitivity_only`
- Smoke/debug 结果永不进入 performance 图表
- 不做 hyperparameter search；不以 GEARS 是否胜出作为 gate 条件

## Git 状态

- `e54132e` Checkpoint Replogle premodel audit before RL1 full runs
- `0a006d8` Fix Replogle RL1 full-run blockers: vocab rebuild, co-expression path, GO-graph trimming
- `da212c4` Take over Replogle RL1 run monitoring
- `902a35d` Add RL1 report writer to postprocess pipeline
- `2278bb0` Update RL1 progress during K562 full run
- `862ef0e` Recover RL1 export after GEARS ctrl_adata fallback
- `d9d8431` Checkpoint RPE1 RL1 training progress
- （当前 RPE1 full run 仍在运行；run 目录与模型权重按仓库策略 gitignored）

## 关键文件索引

| 文件 | 用途 |
|---|---|
| `configs/replogle/gears_rl1_{k562,rpe1}_seed1.yaml` | 冻结配置 |
| `reports/PHASE2A_RL1_CONFIG_DEVIATIONS.md` | 与 Norman 配置差异及理由 |
| `reports/REPLOGLE_RPE1_SMOKE_REPORT.md` | RPE1 smoke PASS 报告 |
| `results/replogle/rl1_split_reproducibility.csv` | 冻结 split 复现验证 |
| `scripts/run_gears_replogle_rl1.py` | full-run runner |
| `scripts/build_gears_rl1_analysis.py` | 下游表/图构建 |
| `scripts/run_rl1_sequencer.sh` | K562→RPE1 自动接力 |
| `scripts/run_rl1_postprocess_when_ready.sh` | 两个 RL1 full run 完成后自动构建表/图并写 RL1 full report + cross-context gate；需从持久终端或下一轮 Codex 启动 |
| `scripts/write_phase2a_rl1_reports.py` | 从 RL1 后处理 CSV 自动写 `PHASE2A_RL1_FULL_REPORT.md` 与 `PHASE2A_CROSS_CONTEXT_GATE.md` |
| `logs/rl1_watch.log` / `logs/rl1_sequencer.log` | 运行监控 |
| `logs/rl1_postprocess.log` | RL1 postprocess watcher 日志 |
