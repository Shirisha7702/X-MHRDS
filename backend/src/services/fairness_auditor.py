import numpy as np
from config import settings as config
from services.fairness_cohort_data import FAIRNESS_SCENARIOS

COHORTS = ["Youth Slang", "Formal Language", "Literal / Direct"]


def _bootstrap_ci(outcomes, n_bootstrap, ci, rng, min_subgroup_size):
    """
    Percentile bootstrap confidence interval (Efron & Tibshirani, 1993) for the mean of a
    0/1 outcome array. Resamples the outcomes with replacement `n_bootstrap` times and takes
    the [alpha/2, 1-alpha/2] percentiles of the resampled means as the CI bounds.

    `meets_min_subgroup_size` is computed on this specific outcome array's own length, since
    e.g. recall is only computed over the true-positive subset of a cohort, which can be
    smaller than the cohort's total size.
    """
    outcomes = np.asarray(outcomes, dtype=float)
    n = len(outcomes)
    meets_min = n >= min_subgroup_size

    if n == 0:
        return {"point": None, "ci_low": None, "ci_high": None, "n": 0, "meets_min_subgroup_size": False}

    point = float(outcomes.mean())
    if n < 2:
        return {"point": point, "ci_low": point, "ci_high": point, "n": n, "meets_min_subgroup_size": meets_min}

    resample_idx = rng.integers(0, n, size=(n_bootstrap, n))
    boot_means = outcomes[resample_idx].mean(axis=1)

    alpha = (1.0 - ci) / 2.0
    ci_low = float(np.percentile(boot_means, alpha * 100))
    ci_high = float(np.percentile(boot_means, (1 - alpha) * 100))
    return {"point": point, "ci_low": ci_low, "ci_high": ci_high, "n": n, "meets_min_subgroup_size": meets_min}


def _intervals_overlap(a, b):
    """Two CIs overlap unless one's upper bound is strictly below the other's lower bound."""
    return not (a["ci_high"] < b["ci_low"] or b["ci_high"] < a["ci_low"])


class FairnessAuditor:
    """
    Audits mental health risk prediction performance across linguistic cohorts (Youth Slang,
    Formal Language, Literal / Direct), each expressing the same set of parallel scenarios so
    cohorts are compared on like-for-like content.

    Beyond per-example correctness, this computes bootstrap 95% CIs for accuracy, recall
    (sensitivity to real risk), and specificity (correctly clearing non-risk text) per cohort,
    gated on a minimum subgroup size (config.FAIRNESS_MIN_SUBGROUP_SIZE) so that metrics
    computed on too few examples are labeled as such rather than reported as if reliable.
    Cohorts are also cross-compared per metric: non-overlapping CIs between two (adequately
    sized) cohorts are flagged as a statistically detectable fairness gap.
    """

    @staticmethod
    def get_cohort_slices():
        """Flattens the parallel scenario table into one row per (scenario, cohort) pair."""
        rows = []
        for scenario in FAIRNESS_SCENARIOS:
            for cohort in COHORTS:
                rows.append({
                    "cohort": cohort,
                    "text": scenario["text"][cohort],
                    "true_label": scenario["true_label"],
                    "scenario_id": scenario["id"],
                })
        return rows

    def audit_model(self, predict_proba_fn, min_subgroup_size=None, n_bootstrap=None, ci=0.95, random_state=None):
        """
        Runs the cohort audit and returns per-example predictions plus, for each cohort,
        bootstrap-CI'd accuracy/recall/specificity and any detected cross-cohort fairness gaps.

        Args:
            predict_proba_fn: callable(text) -> [prob_non_risk, prob_risk].
            min_subgroup_size: minimum n to trust a metric's CI. Defaults to
                config.FAIRNESS_MIN_SUBGROUP_SIZE.
            n_bootstrap: bootstrap resample count. Defaults to config.FAIRNESS_BOOTSTRAP_ITERATIONS.
            ci: confidence level (0.95 = 95% CI).
            random_state: RNG seed for reproducible resampling. Defaults to config.RANDOM_STATE.

        Returns:
            dict with "min_subgroup_size", "examples" (per-example rows), "cohort_summary"
            (per-cohort accuracy/recall/specificity with CIs), and "fairness_gaps" (cross-cohort
            non-overlapping-CI flags).
        """
        min_subgroup_size = config.FAIRNESS_MIN_SUBGROUP_SIZE if min_subgroup_size is None else min_subgroup_size
        n_bootstrap = config.FAIRNESS_BOOTSTRAP_ITERATIONS if n_bootstrap is None else n_bootstrap
        random_state = config.RANDOM_STATE if random_state is None else random_state
        rng = np.random.default_rng(random_state)

        slices = self.get_cohort_slices()
        examples = []
        by_cohort = {cohort: [] for cohort in COHORTS}

        for item in slices:
            text = item["text"]
            true_label = item["true_label"]
            cohort = item["cohort"]

            probs = predict_proba_fn(text)
            prob_risk = float(probs[1])
            pred_label = 1 if prob_risk >= 0.5 else 0

            error_status = "Correct"
            if true_label == 1 and pred_label == 0:
                error_status = "False Negative (MISS)"
            elif true_label == 0 and pred_label == 1:
                error_status = "False Positive (FALSE ALARM)"

            examples.append({
                "Cohort": cohort,
                "Text": text,
                "True Label": "Risk" if true_label == 1 else "Non-Risk",
                "Predicted Label": "Risk" if pred_label == 1 else "Non-Risk",
                "Risk Probability": f"{prob_risk * 100:.2f}%",
                "Status": error_status,
            })
            by_cohort[cohort].append((true_label, pred_label))

        cohort_summary = []
        metrics_by_cohort = {}
        for cohort in COHORTS:
            pairs = by_cohort[cohort]

            accuracy_outcomes = [1.0 if true == pred else 0.0 for true, pred in pairs]
            recall_outcomes = [1.0 if pred == 1 else 0.0 for true, pred in pairs if true == 1]
            specificity_outcomes = [1.0 if pred == 0 else 0.0 for true, pred in pairs if true == 0]

            metrics = {
                "accuracy": _bootstrap_ci(accuracy_outcomes, n_bootstrap, ci, rng, min_subgroup_size),
                "recall": _bootstrap_ci(recall_outcomes, n_bootstrap, ci, rng, min_subgroup_size),
                "specificity": _bootstrap_ci(specificity_outcomes, n_bootstrap, ci, rng, min_subgroup_size),
            }
            metrics_by_cohort[cohort] = metrics
            cohort_summary.append({"cohort": cohort, "n": len(pairs), **metrics})

        fairness_gaps = []
        for metric in ("accuracy", "recall", "specificity"):
            for i in range(len(COHORTS)):
                for j in range(i + 1, len(COHORTS)):
                    cohort_a, cohort_b = COHORTS[i], COHORTS[j]
                    stats_a = metrics_by_cohort[cohort_a][metric]
                    stats_b = metrics_by_cohort[cohort_b][metric]

                    if not (stats_a["meets_min_subgroup_size"] and stats_b["meets_min_subgroup_size"]):
                        continue
                    if not _intervals_overlap(stats_a, stats_b):
                        fairness_gaps.append({
                            "metric": metric,
                            "cohort_a": cohort_a,
                            "cohort_a_ci": [stats_a["ci_low"], stats_a["ci_high"]],
                            "cohort_b": cohort_b,
                            "cohort_b_ci": [stats_b["ci_low"], stats_b["ci_high"]],
                        })

        return {
            "min_subgroup_size": min_subgroup_size,
            "examples": examples,
            "cohort_summary": cohort_summary,
            "fairness_gaps": fairness_gaps,
        }


if __name__ == "__main__":
    # Mock predict proba: flags anything mentioning ending life / hopelessness as risk.
    def mock_predict(text):
        risk_markers = ("end my life", "end it", "wake up", "disappear", "burden")
        is_risk = any(marker in text.lower() for marker in risk_markers)
        return [0.15, 0.85] if is_risk else [0.9, 0.1]

    auditor = FairnessAuditor()
    result = auditor.audit_model(mock_predict)

    print(f"Min subgroup size: {result['min_subgroup_size']}\n")
    for row in result["cohort_summary"]:
        print(f"Cohort: {row['cohort']} (n={row['n']})")
        for metric in ("accuracy", "recall", "specificity"):
            m = row[metric]
            flag = "" if m["meets_min_subgroup_size"] else "  [insufficient sample]"
            print(f"  {metric}: {m['point']:.2f}  95% CI [{m['ci_low']:.2f}, {m['ci_high']:.2f}] (n={m['n']}){flag}")
        print()

    print(f"Fairness gaps detected: {len(result['fairness_gaps'])}")
    for gap in result["fairness_gaps"]:
        print(f"  {gap['metric']}: {gap['cohort_a']} {gap['cohort_a_ci']} vs {gap['cohort_b']} {gap['cohort_b_ci']}")
