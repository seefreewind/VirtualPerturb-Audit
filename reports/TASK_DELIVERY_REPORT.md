# 任务交付报告 — VirtualPerturb-Audit Pilot 收尾执行

- 交付日期：2026-08-23
- 任务来源：`reports/NEXT_TASKS_AND_DELIVERABLES.md`（2026-08-22 版）
- 执行环境：本机 Mac CPU（`environment/gears-venv` 隔离环境）

## 一、任务完成情况总览

| 优先级 | 任务 | 结果 |
|---|---|---|
| P0 | 完成 GEARS L2 全量评估（CPU） | ✅ 完成 |
| P0 | 完成 GEARS L3 全量评估（CPU） | ✅ 完成 |
| P0 | 重建下游审计输出（tables/figures/tests） | ✅ 完成 |
| P1 | gemgroup 空包络敏感性扩展到 GEARS 行 | ✅ 完成 |
| P1 | 更新决策报告（PILOT_DECISION/PROJECT_STATUS/CHANGELOG/NEXT_ACTIONS） | ✅ 完成 |
| P1 | 提交 GEARS 最终产物 | ✅ 完成 |
| P2 | 失败 L2 运行目录处置 | ✅ 完成（保留并显式标记 FAILED_GEARS） |

## 二、GEARS 全量评估结果（核心交付）

| Split | 运行目录 | 测试扰动数 | 耗时（秒） | 状态 |
|---|---|---|---|---|
| L1 | `results/pilot/gears_20260822T065552Z/` | 55 | 18,284 | `COMPLETED_GEARS_EVALUATION` |
| L2 | `results/pilot/gears_20260822T122126Z/` | 40 | 17,987 | `COMPLETED_GEARS_EVALUATION` |
| L3 | `results/pilot/gears_20260822T172146Z/` | 25 | 21,057 | `COMPLETED_GEARS_EVALUATION` |

每个运行目录包含：`gears_metrics.csv`、`gears_delta_centroids.pt`、`gears_perturbation_retrieval.csv`、`metadata.json`（权重目录按 `.gitignore` 排除）。

### 指标摘要

| Split | Pearson Δ (95% CI) | UER@50 | 符号翻转率 | 检索 Top-1 | 检索 Top-5 | MRR | BNS |
|---|---|---|---|---|---|---|---|
| L1 | 0.9887 (0.9860–0.9914) | 0.0 | 0.0 | 0.200 | 0.491 | 0.328 | UNVERIFIED |
| L2 | 0.9838 (0.9795–0.9875) | 0.0 | 0.0 | 0.075 | 0.150 | 0.147 | UNVERIFIED |
| L3 | 0.9843 (0.9781–0.9896) | 0.0 | 0.0 | 0.080 | 0.320 | 0.207 | UNVERIFIED |

**核心发现**：delta-Pearson 在各 split 保持高值（≈0.98–0.99），但扰动检索在严格留出设置下崩塌（Top-1：0.20 → 0.075 → 0.08；MRR：0.328 → 0.147 → 0.207）。"相关性稳定、检索崩塌"的解离模式与 shortcut/leakage 审计假设一致，是本 pilot 最值得写入手稿的信号。

## 三、下游输出重建

- `results/pilot/pilot_summary.csv` — 含 GEARS L1/L2/L3 全量行（`COMPLETED_GEARS_EVALUATION`）
- `results/pilot/perturbation_retrieval.csv` — 含 GEARS 检索行
- `results/pilot/null_envelope_sensitivity.csv` — 新增 GEARS 行（L1 0.172 / L2 0.262 / L3 0.235，q95 gemgroup 空包络）
- `results/tables/table2_models.*` — GEARS 状态更新为 `FULL_EVALUATION_COMPLETED_L1_L2_L3_PILOT`
- `results/tables/table5_primary_pilot_metrics.*`、`table6_null_envelope_sensitivity.*` — 重建并含 GEARS 行
- `figures/main/pilot_truthfulness.*`、`pilot_hallucination.*` — 重建；性能图中已排除 smoke 行
- 验证：`build_tables.py`、`build_figures.py` 运行无错；`pytest` 10/10 通过

## 四、脚本改动

- `scripts/run_null_envelope_sensitivity.py` — 新增 `completed_gears_pred_deltas()` 与 `gears_sensitivity_rows()`：
  - 按 `metadata.json` 中 `summary_row.status == COMPLETED_GEARS_EVALUATION` 自动发现 GEARS 全量运行
  - 条件名 canonical 对齐（`ctrl+X` 与 `X+ctrl` 等价）
  - GEARS 原始预测经审计对照均值转换到 audit-delta 空间，与基线同口径比较
- `scripts/build_tables.py` — table 2 GEARS 状态更新
- `scripts/build_figures.py` — 排除 `SMOKE` 行，避免把有限 smoke 行当作模型性能

## 五、报告与提交

- 报告更新：`reports/PILOT_DECISION.md`（决策：`PROVISIONAL_GO_FOR_BASELINE_AUDIT; GEARS_FULL_EVALUATION_COMPLETED_PILOT (BNS unverified)`）、`PROJECT_STATUS.md`、`CHANGELOG.md`、`NEXT_ACTIONS.md`、`reports/FINAL_PILOT_RESULT_REPORT.md`（本报告姊妹篇，英文）
- Git 提交：
  - `a2885cf` Complete GEARS L1/L2/L3 full CPU evaluation and rebuild downstream outputs（46 文件）
  - `b470772` Add final pilot result report
  - 当前 worktree clean（忽略项：raw data、venv、logs、模型权重目录）

## 六、失败与处置记录（P2）

- `results/pilot/gears_20260822T120129Z/` — L2 首次尝试失败（`BrokenPipeError`，825 秒，stdout 管道中断；非模型/数据问题）。保留目录并显式 `status: FAILED_GEARS` + traceback，不可被误认为完成结果。重跑已成功。
- `results/pilot/gears_20260822T065423Z/` — L1 CUDA 不可用失败尝试，同样保留显式失败状态。

## 七、解释护栏（全部遵守）

- 不把 smoke 行当作模型性能
- 仅对 `COMPLETED_GEARS_EVALUATION` 行解读 GEARS
- BNS 保持 `UNVERIFIED`（无真实生物学重复标签）
- GEO `gemgroup` 视为 batch-like 敏感性元数据，非生物学重复
- 不确定性按扰动级 bootstrap 报告，不用细胞级计数制造虚假精度

## 八、遗留事项（供后续决策）

1. 将"L1 可检索、L2/L3 检索崩塌、相关度稳定"模式写入稿件作为核心 shortcut 审计发现
2. BNS 上界在找到真实重复标签前保持 UNVERIFIED；gemgroup 敏感性仅作 batch-like 灵敏度
3. 若需要精确 GEARS 性能数字，需 GPU 或 prediction-only 复现