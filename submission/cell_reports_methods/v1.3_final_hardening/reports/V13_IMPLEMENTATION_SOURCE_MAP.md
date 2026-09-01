# v1.3 Implementation Source Map

No material implementation bug affecting the locked results was detected.

| method_name | source_file | function | line/range | inputs | outputs | parameters | frozen version | manuscript description matches code? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Retrieval | src/metrics/retrieval.py | perturbation_centroid_retrieval; perturbation_retrieval_rows | 7-49 | pred_centroids dict; true_centroids dict | top1/top5/mrr plus per-target rank | cosine_similarity; candidate intersection; no standardization | Frozen v1.3 | YES |
| STATE retrieval | scripts/build_state_phase2c_analysis.py | retrieval_rows | 179-216 | pred_delta/truth_delta dictionaries | rank/top1/top5/mrr per target | manual cosine; finite shared labels; zero-vector guard | Frozen Phase 2C | YES |
| UER | src/hallucination/metrics.py | unsupported_effect_rate_at_k | 6-11 | pred_delta, true_delta, k, null_abs_threshold | UER@K | top abs(pred_delta); unsupported if abs(true_delta)<=threshold | Frozen v1.3 | YES |
| Sign flip | src/hallucination/metrics.py | sign_flip_rate | 14-26 | pred_delta, true_delta, support_threshold | sign_flip_rate; major_sign_flip_rate; n_supported_genes | supported genes abs(true)>threshold; sign mismatch | Frozen v1.3 | YES |
| Split L0 | src/splits/builders.py | assign_l0_random_cells | 25-34 | AnnData obs; fractions; seed | cell-level train/val/test labels | random cell holdout | Frozen v1.3 | YES |
| Split L1 | src/splits/builders.py | assign_l1_unseen_perturbations | 37-56 | perturbation labels; fractions; seed | target-level holdout labels | controls train; non-control perturbations held out | Frozen v1.3 | YES |
| Split L2 | src/splits/builders.py | assign_l2_component_holdout | 59-82 | perturbation components; fractions; seed | component holdout labels plus overlap exclusions | all components must belong to held-out set; mixed overlap excluded | Frozen v1.3 | YES |
| Split L3 | src/splits/builders.py | assign_l3_gene_family_holdout | 85-127 | HGNC-derived gene family groups; perturbation labels | gene-family holdout labels plus overlap exclusions | candidate file results/pilot/l3_gene_family_holdout_candidates.csv | Frozen v1.3 | YES |
| Split R-L1 | src/splits/builders.py | assign_replogle_r_l1 | 130-163 | cell_line; perturbation labels; seed | within-context target holdout | non-selected context excluded | Frozen v1.3 | YES |
| Split R-L4 | src/splits/builders.py | assign_replogle_r_l4 | 166-190 | train_context; target_context; eligible_targets | cross-context train/test/exclude labels | source-context perturbations train; target-context perturbations and controls test | Frozen v1.3 | YES |
| Baselines B0-B4 | src/models/baselines.py | NoChangeBaseline; GlobalPerturbedMeanBaseline; ContextMatchedMeanBaseline; PCARidgeBaseline | 9-65 | training expression/features/context | predicted expression or delta | no-change, mean, context mean, PCA/Ridge | Frozen v1.3 | YES |
| Replogle probes | scripts/run_replogle_baseline_audit.py | evaluate_setting; summarize | 74-191 | frozen Replogle train/test deltas | GEARS/baseline/probe endpoint rows | B3/FP2 unavailable in Replogle essential-screen setting | Frozen v1.3 | YES |
| Matched-target analysis | scripts/build_phase2b_matched_sensitivity.py | build_sensitivity; comparison_frame; summarize_metric | 232-315 | frozen target-level metrics and matched registry | paired difference and bootstrap interval | 2000 paired bootstrap resamples; common-candidate retrieval when vectors exist | Frozen Phase 2B | YES |
