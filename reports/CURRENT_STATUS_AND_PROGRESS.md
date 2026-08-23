# VirtualPerturb-Audit 当前整体情况与工作进度

更新时间：2026-08-23

## 一句话结论

项目主体审计流程已经跑通，Norman 数据集上的 baseline、falsification probes、L1/L2/L3 严格划分、GEARS full CPU evaluation、下游表格和图表均已完成。当前可以进入论文/报告写作阶段，但所有 GEARS 结果仍需带着 `bns_status: UNVERIFIED` 解释，因为尚未找到可作为真实生物重复的标签。

## 当前阶段判断

当前状态：`PROVISIONAL_GO_FOR_BASELINE_AUDIT; GEARS_FULL_EVALUATION_COMPLETED_PILOT (BNS unverified)`

这意味着：

- 可以使用现有结果支撑 pilot 级别的 shortcut/leakage audit 叙事。
- 可以把 GEARS L1/L2/L3 完整结果作为核心模型审计结果纳入写作。
- 不能把 BNS 或 replicate-derived upper bound 作为已验证性能边界来宣称。
- `gemgroup` 只能作为 batch-like sensitivity metadata 使用，不能当作真实 biological replicate。

## 已完成工作

### 1. 项目与环境

- 项目仓库已建立并持续使用现有 Git repository。
- Python 运行环境、GEARS 隔离环境、依赖记录和环境报告已完成。
- `cell-gears==0.1.2`、`torch-geometric==2.6.1` 已在 `environment/gears-venv` 中安装并验证可用。
- 当前测试通过：`10 passed`。

### 2. 数据获取与 QC

- Norman GEARS-format AnnData 已获取并完成本地校验。
- 数据规模：
  - 91,205 cells
  - 5,045 genes
  - 284 perturbations
  - 7,353 controls
- GEO metadata link audit 已完成，88,843 / 91,205 GEARS cells 可匹配到 GEO metadata。
- `gemgroup` 覆盖率高，但只能作为 batch-like sensitivity 字段。

### 3. 数据划分与完整性检查

- L0/L1/L2 划分已实现并通过 integrity checks。
- L3 HGNC gene-family holdout 已实现，并整合进：
  - split integrity
  - baseline pilot
  - falsification probes
  - FP3 permutation
  - null-envelope sensitivity
  - retrieval/confusion analysis
  - primary metric tables
- replicate-label audit 已完成，未发现可靠 biological replicate label。

### 4. Baseline 与 falsification probes

已完成的 baseline/probe 包括：

- B0 no-change
- B1 global perturbed mean
- B2 context-matched perturbed mean
- B3 additive seen-component
- B4 PCA/Ridge
- B5 mean-effect baseline
- FP-1 perturbation-blind mean-effect
- FP-2 cell-state-blind additive
- FP-3 label-shuffled mean-effect，已完成 20 permutations

这些结果已汇总到 `results/pilot/pilot_summary.csv` 及相关下游表格中。

### 5. GEARS full CPU evaluation

GEARS 已在本机 CPU 上完成 L1/L2/L3 full evaluation，设置为 20 epochs、seed 1、`essential` perturbation graph。

| Split | Run folder | Test perturbations | Elapsed | Status |
|---|---|---:|---:|---|
| L1 | `results/pilot/gears_20260822T065552Z/` | 55 | 18,284 s | `COMPLETED_GEARS_EVALUATION` |
| L2 | `results/pilot/gears_20260822T122126Z/` | 40 | 17,987 s | `COMPLETED_GEARS_EVALUATION` |
| L3 | `results/pilot/gears_20260822T172146Z/` | 25 | 21,057 s | `COMPLETED_GEARS_EVALUATION` |

每个 run folder 中均包含：

- `gears_metrics.csv`
- `gears_delta_centroids.pt`
- `gears_perturbation_retrieval.csv`
- `metadata.json`

失败尝试也已保留为 provenance：

- `results/pilot/gears_20260822T065423Z/`：CUDA attempt failed，`FAILED_GEARS`
- `results/pilot/gears_20260822T120129Z/`：L2 background/pipe attempt failed，`BrokenPipeError`，后续 foreground rerun 已成功

## 核心结果

### GEARS full evaluation 指标

| Split | n | Pearson delta | 95% CI | Retrieval top-1 | Retrieval top-5 | MRR | BNS |
|---|---:|---:|---|---:|---:|---:|---|
| L1 | 55 | 0.988748 | 0.986001-0.991368 | 0.200 | 0.490909 | 0.327747 | `UNVERIFIED` |
| L2 | 40 | 0.983792 | 0.979453-0.987480 | 0.075 | 0.150000 | 0.147070 | `UNVERIFIED` |
| L3 | 25 | 0.984334 | 0.978093-0.989626 | 0.080 | 0.320000 | 0.206694 | `UNVERIFIED` |

### 主要科学信号

最重要的 pilot 发现是：

GEARS 在 L1/L2/L3 中都保持很高的 delta-Pearson，大约 0.98-0.99；但 perturbation retrieval 在更严格 holdout 下明显下降，top-1 从 L1 的 0.20 降到 L2 的 0.075 和 L3 的 0.08。

这说明模型可以维持较高的整体表达扰动相关性，但 exact-condition identity / perturbation-specific retrieval 在 component-held-out 和 gene-family-held-out 设置下显著受损。这个“高相关 + retrieval collapse”的分离现象，是当前项目最适合写入 manuscript 的 shortcut/leakage audit 主线。

## 已生成和已验证的关键产物

### 结果文件

- `results/pilot/pilot_summary.csv`：37 rows x 21 cols
- `results/pilot/perturbation_retrieval.csv`：2853 rows x 9 cols
- `results/pilot/seed_robustness_summary.csv`：24 rows x 21 cols
- `results/pilot/null_envelope_sensitivity.csv`：30 rows x 8 cols
- `results/pilot/gene_family_confusion_summary.csv`：29 rows x 9 cols
- `reports/replicate_label_audit.tsv`：4 rows x 7 cols

### 报告文件

- `reports/FINAL_PILOT_RESULT_REPORT.md`
- `reports/TASK_DELIVERY_REPORT.md`
- `reports/GEARS_FULL_RUN_HANDOFF.md`
- `reports/NORMAN_ACQUISITION_REPORT.md`
- `reports/REVIEWER_ATTACK_AUDIT.md`
- `reports/replicate_label_audit.md`
- `PROJECT_STATUS.md`
- `NEXT_ACTIONS.md`
- `CHANGELOG.md`

### 表格与图

已重建：

- `results/tables/table2_models.*`
- `results/tables/table5_primary_pilot_metrics.*`
- `results/tables/table6_null_envelope_sensitivity.*`
- `figures/main/pilot_truthfulness.*`
- `figures/main/pilot_hallucination.*`

注意：smoke rows 已从 performance figures 中排除，避免把软件连通性检查误读为模型性能。

## 当前 Git 状态

最近关键提交：

- `b470772 Add final pilot result report`
- `a2885cf Complete GEARS L1/L2/L3 full CPU evaluation and rebuild downstream outputs`
- `3125e1e Add next tasks and deliverables handoff`

当前仍有未跟踪文件：

- `reports/TASK_DELIVERY_REPORT.md`
- `../.DS_Store`

其中 `reports/TASK_DELIVERY_REPORT.md` 是交付说明类文件，可以根据是否需要纳入版本管理决定是否提交；`.DS_Store` 是 macOS 自动文件，建议忽略。

## 当前风险与限制

1. BNS 未验证

   没有找到可靠 biological replicate label，因此不能把 BNS upper bound 当作已验证边界。所有相关结果应保留 `bns_status: UNVERIFIED`。

2. `gemgroup` 只能作为 sensitivity metadata

   `gemgroup` 可用于 batch-like null-envelope sensitivity，但不能当作 replicate-derived biological null。

3. GEARS CPU 训练成本高

   每个 full split 在本机 CPU 上约 5-6 小时。后续如果需要复现实验，优先考虑 GPU 或 prediction-only replication。

4. GEARS vocabulary 与 audit splitter vocabulary 存在轻微差异

   GEARS 内部 condition 命名和测试集合与 audit splitter 不完全一致，例如 `ctrl+X` 与 `X+ctrl` 顺序问题。当前指标是在 GEARS-run vocabulary 内计算，写作时需要说明。

5. GEARS GO graph 来源需要谨慎描述

   官方 tarball endpoint 曾返回不可用内容，当前 run 使用从本地 GEARS prior files 生成的 filtered GO tensor。方法部分需要准确写明。

## 下一步建议

### P0：论文/报告主线整理

- 把 “stable delta-Pearson + collapsing retrieval under L2/L3” 作为主结果。
- 明确区分：
  - predictive similarity / delta-Pearson
  - perturbation identity retrieval
  - shortcut/leakage audit signal
- 避免把高 Pearson 写成严格泛化成功。

### P1：BNS 与 sensitivity 边界写清楚

- 保留所有 `bns_status: UNVERIFIED`。
- 将 gemgroup null-envelope 写为 sensitivity analysis。
- 不声称 replicate-derived upper bound 已建立。

### P2：可选复现实验

如果后续要对 GEARS 具体数值提出更强 claim，建议补做：

- GPU 上 L1/L2/L3 复跑，或
- 固定 checkpoint / prediction-only replication，或
- seed-level GEARS replication。

### P3：手稿产物

可以开始准备：

- manuscript outline
- Results section draft
- Methods section draft
- Figure/table legend
- limitation paragraph
- reviewer-facing robustness checklist

## 当前可交付状态

当前项目已经具备以下可交付内容：

- 可复核的 pilot result tables
- 可复核的 GEARS full-run metadata
- 可用于论文主结果的 L1/L2/L3 comparison
- 可用于补充材料的 null-envelope sensitivity、seed robustness、gene-family confusion analysis
- 可解释失败尝试的 provenance
- 已通过的测试记录

总体判断：当前不是“还没完成实验”的阶段，而是“实验主体已完成，进入写作、解释边界收紧和可选复现”的阶段。
