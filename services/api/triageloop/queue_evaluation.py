"""Paired Queue Twin experiment runner and bootstrap evidence."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path

import numpy as np

from .features import load_encounters
from .queueing import (
    SIMULATION_VERSION,
    SimulationResult,
    build_template_library,
    create_shift,
    load_site_profiles,
    simulate_shift,
)
from .recommendation import ModelBundle


POLICIES = ("fifo", "static", "triageloop")
SCALAR_METRICS = (
    "arrivals",
    "critical_cases",
    "action_window_miss_rate",
    "unsafe_undertriage_rate",
    "critical_recall",
    "mean_signal_to_action_minutes",
    "negative_slack_minutes",
    "median_wait_minutes",
    "low_acuity_p90_wait_minutes",
    "waiting_time_effectiveness",
    "rank_triage_effectiveness",
    "throughput_within_shift",
    "max_queue_length",
    "capacity_conflict_rate",
    "consolidated_alerts",
    "alerts_per_waiting_patient_hour",
    "alerts_per_reassessment_nurse_hour",
)


def _aggregate(rows: list[SimulationResult]) -> dict[str, object]:
    result = {metric: float(np.mean([getattr(row, metric) for row in rows])) for metric in SCALAR_METRICS}
    resource_names = rows[0].utilization
    result["utilization"] = {name: float(np.mean([row.utilization[name] for row in rows])) for name in resource_names}
    result["replications"] = len(rows)
    return result


def _bootstrap_relative(
    static: np.ndarray,
    triageloop: np.ndarray,
    *,
    lower_is_better: bool,
    seed: int,
    samples: int = 1000,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(samples):
        indices = rng.integers(0, len(static), size=len(static))
        baseline = float(np.mean(static[indices]))
        candidate = float(np.mean(triageloop[indices]))
        if abs(baseline) < 1e-12:
            estimate = 0.0
        else:
            estimate = (baseline - candidate) / baseline if lower_is_better else (candidate - baseline) / baseline
        estimates.append(estimate)
    baseline = float(np.mean(static))
    candidate = float(np.mean(triageloop))
    point = (baseline - candidate) / baseline if lower_is_better and baseline else (candidate - baseline) / baseline if baseline else 0.0
    return {
        "static_mean": baseline,
        "triageloop_mean": candidate,
        "relative_improvement": point,
        "ci95_low": float(np.quantile(estimates, 0.025)),
        "ci95_high": float(np.quantile(estimates, 0.975)),
    }


def run_queue_experiments(
    root: Path,
    *,
    replications: int = 100,
    base_seed: int = 20260822,
) -> dict[str, object]:
    profiles, shift_minutes, loads, response_minutes = load_site_profiles(root / "data" / "specs" / "site-profiles.json")
    bundle = ModelBundle.from_path(root / "artifacts" / "models" / "tl-02" / "selected-model.json")
    templates = build_template_library(
        load_encounters(root / "data" / "generated" / "encounters.jsonl"),
        bundle,
        response_minutes,
    )
    rows: list[SimulationResult] = []
    for site_index, (site_name, profile) in enumerate(profiles.items()):
        for load_index, (load_name, multiplier) in enumerate(loads.items()):
            for repetition in range(replications):
                seed = base_seed + site_index * 100_000 + load_index * 10_000 + repetition
                tasks, triage_utilization = create_shift(profile, multiplier, shift_minutes, templates, seed)
                for policy in POLICIES:
                    rows.append(
                        simulate_shift(
                            tasks,
                            profile,
                            shift_minutes,
                            load_name,
                            policy,
                            seed,
                            triage_utilization,
                        )
                    )

    cells = {}
    for site_name in profiles:
        for load_name in loads:
            for policy in POLICIES:
                cell_rows = [row for row in rows if row.site == site_name and row.load_state == load_name and row.policy == policy]
                cells[f"{site_name}|{load_name}|{policy}"] = _aggregate(cell_rows)

    paired = {}
    for site_name in profiles:
        for load_name in loads:
            for metric, lower_is_better in (
                ("action_window_miss_rate", True),
                ("negative_slack_minutes", True),
                ("mean_signal_to_action_minutes", True),
                ("low_acuity_p90_wait_minutes", True),
                ("waiting_time_effectiveness", False),
                ("rank_triage_effectiveness", False),
            ):
                static = np.asarray([getattr(row, metric) for row in rows if row.site == site_name and row.load_state == load_name and row.policy == "static"])
                triageloop = np.asarray([getattr(row, metric) for row in rows if row.site == site_name and row.load_state == load_name and row.policy == "triageloop"])
                paired[f"{site_name}|{load_name}|{metric}"] = _bootstrap_relative(
                    static,
                    triageloop,
                    lower_is_better=lower_is_better,
                    seed=base_seed + len(paired),
                )

    surge_static = [row for row in rows if row.load_state == "surge_3x" and row.policy == "static"]
    surge_triage = [row for row in rows if row.load_state == "surge_3x" and row.policy == "triageloop"]
    overall_surge = {}
    for metric, lower_is_better in (
        ("action_window_miss_rate", True),
        ("negative_slack_minutes", True),
        ("mean_signal_to_action_minutes", True),
        ("low_acuity_p90_wait_minutes", True),
    ):
        overall_surge[metric] = _bootstrap_relative(
            np.asarray([getattr(row, metric) for row in surge_static]),
            np.asarray([getattr(row, metric) for row in surge_triage]),
            lower_is_better=lower_is_better,
            seed=base_seed + 900 + len(overall_surge),
        )

    response_sensitivity = {}
    for response_allowance in (10, 20, 30):
        adjusted_templates = []
        for template in templates:
            if not template.critical:
                adjusted_templates.append(template)
                continue
            deadline = float((template.deterioration_signal_minutes or 0) + response_allowance)
            hard_deadlines = ([5.0] if template.initial_hard_rule else []) + [
                elapsed + 5.0 for elapsed, _predicted, _risk, hard, _uncertain in template.updates if hard
            ]
            if hard_deadlines:
                deadline = min(deadline, min(hard_deadlines))
            adjusted_templates.append(replace(template, true_deadline_minutes=deadline))
        sensitivity_static = []
        sensitivity_triage = []
        for site_index, profile in enumerate(profiles.values()):
            for repetition in range(30):
                seed = base_seed + 700_000 + response_allowance * 1_000 + site_index * 100 + repetition
                tasks, triage_utilization = create_shift(profile, loads["surge_3x"], shift_minutes, adjusted_templates, seed)
                sensitivity_static.append(simulate_shift(tasks, profile, shift_minutes, "surge_3x", "static", seed, triage_utilization).action_window_miss_rate)
                sensitivity_triage.append(simulate_shift(tasks, profile, shift_minutes, "surge_3x", "triageloop", seed, triage_utilization).action_window_miss_rate)
        response_sensitivity[str(response_allowance)] = _bootstrap_relative(
            np.asarray(sensitivity_static),
            np.asarray(sensitivity_triage),
            lower_is_better=True,
            seed=base_seed + 800_000 + response_allowance,
        )

    gates = {
        "surge_action_window_relative_reduction_at_least_20pct": overall_surge["action_window_miss_rate"]["relative_improvement"] >= 0.20,
        "low_acuity_p90_no_more_than_20pct_worse": overall_surge["low_acuity_p90_wait_minutes"]["triageloop_mean"] <= 1.20 * overall_surge["low_acuity_p90_wait_minutes"]["static_mean"],
        "all_cells_have_100_replications": all(cell["replications"] == replications for cell in cells.values()),
    }
    alert_workload = {
        site_name: {
            load_name: {
                "reassessment_nurses": profiles[site_name].reassessment_nurses,
                "mean_consolidated_alerts_per_8h_shift": cells[f"{site_name}|{load_name}|triageloop"]["consolidated_alerts"],
                "mean_alerts_per_reassessment_nurse_hour": cells[f"{site_name}|{load_name}|triageloop"]["alerts_per_reassessment_nurse_hour"],
            }
            for load_name in loads
        }
        for site_name in profiles
    }
    evaluation_dir = root / "artifacts" / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    shift_path = evaluation_dir / "tl-03-shifts.jsonl"
    with shift_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(asdict(row), sort_keys=True) + "\n")
    config_checksum = hashlib.sha256((root / "data" / "specs" / "site-profiles.json").read_bytes()).hexdigest()
    results = {
        "simulation_version": SIMULATION_VERSION,
        "base_seed": base_seed,
        "replications_per_cell": replications,
        "site_profiles": list(profiles),
        "load_states": loads,
        "policies": list(POLICIES),
        "template_count": len(templates),
        "total_policy_shifts": len(rows),
        "configuration_sha256": config_checksum,
        "cells": cells,
        "paired_comparisons": paired,
        "overall_surge": overall_surge,
        "deterioration_response_sensitivity": response_sensitivity,
        "alert_workload": alert_workload,
        "gates": gates,
        "synthetic_simulation_only": True,
        "not_for_clinical_or_staffing_use": True,
    }
    (evaluation_dir / "tl-03-queue-metrics.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results
