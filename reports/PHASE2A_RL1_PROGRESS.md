# Phase 2A-RL1 当前进度报告

更新时间：2026-08-24 20:10 (CST)

## 总体状态

```text
Norman pilot:                COMPLETE_AND_FROZEN（不重算）
Replogle Phase 2A:           CONDITIONAL_GO_GEARS_FILTERED
BNS:                         UNVERIFIED（本阶段不变）
RPE1 bounded smoke:          PASS（executable chain 证据，非性能）
R-L1-K562 full run:          RUNNING（Epoch 9/20，约 30 分钟/epoch）
R-L1-RPE1 full run:          QUEUED（K562 完成后由 sequencer 自动启动）
Norman/Replogle comparison:  PENDING（等待两个 full run）
Cross-context gate:          PENDING
```

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
| 运行目录 | `results/replogle/gears/rl1_k562_20260824T074041Z/` |
| 数据集 | Replogle_K562_GEARS_filtered（filtered essential-screen data） |
| Split | R-L1-K562（frozen hash 已验证） |
| 进度 | Epoch 9/20（20:02 时 Step 1001），约 30 min/epoch |
| 训练损失趋势 | epoch MSE 0.0089 → 0.0087 → 0.0080（正常下降） |
| 资源 | ~230% CPU，无 swap 压力 |
| 预计 K562 完成 | 2026-08-25 约 01:30–03:00 CST |
| 预计 RPE1 完成 | 2026-08-25 上午至中午（自动接力，~8h） |

### 中断事件记录（已处置）

- 2026-08-23 22:33 机器重启（内存压力+并发任务导致），第一次 K562 run 于 epoch 7 被杀。
  - 该次运行已显式标记 `FAILED_GEARS_INTERRUPTED_SYSTEM_REBOOT`（provenance，不可误认为完成结果）
  - pyg cache / GO csv / co-expression csv 均保留，重跑无需重建
  - 2026-08-24 15:40 重新启动，当前 run 即为重启后的干净重跑

## 待办（按序）

1. 等 K562 full run 完成（自动）→ 校验 metadata/metrics 输出
2. sequencer 自动启动 R-L1-RPE1 full run → 完成校验
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
- （工作树 clean；run 目录与模型权重按仓库策略 gitignored）

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
| `logs/rl1_watch.log` / `logs/rl1_sequencer.log` | 运行监控 |
