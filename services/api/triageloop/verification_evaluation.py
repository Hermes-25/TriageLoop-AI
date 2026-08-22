"""TL-05 verification experiments kept separate from registered TL-03 evidence."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path

import numpy as np

from .features import load_encounters
from .queue_evaluation import SCALAR_METRICS, _aggregate, _bootstrap_relative
from .queueing import (
    SIMULATION_VERSION,
    SimulationResult,
    build_template_library,
    create_shift,
    load_site_profiles,
    simulate_shift,
)
from .recommendation import ModelBundle


VERIFICATION_POLICIES = ("static_periodic", "triageloop")
COMPARISON_METRICS = (
    ("action_window_miss_rate", True),
    ("negative_slack_minutes", True),
    ("mean_signal_to_action_minutes", True),
    ("low_acuity_p90_wait_minutes", True),
    ("waiting_time_effectiveness", False),
    ("rank_triage_effectiveness", False),
)


def _templates_with_response_allowance(templates: list, response_allowance: int) -> list:
    adjusted = []
    for template in templates:
        if not template.critical:
            adjusted.append(template)
            continue
        deadline = float((template.deterioration_signal_minutes or 0) + response_allowance)
        hard_deadlines = ([5.0] if template.initial_hard_rule else []) + [
            elapsed + 5.0 for elapsed, _predicted, _risk, hard, _uncertain in template.updates if hard
        ]
        if hard_deadlines:
            deadline = min(deadline, min(hard_deadlines))
        adjusted.append(replace(template, true_deadline_minutes=deadline))
    return adjusted


def run_periodic_retriage_experiment(
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
                for policy in VERIFICATION_POLICIES:
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

    cells = {
        f"{site_name}|{load_name}|{policy}": _aggregate(
            [row for row in rows if row.site == site_name and row.load_state == load_name and row.policy == policy]
        )
        for site_name in profiles
        for load_name in loads
        for policy in VERIFICATION_POLICIES
    }
    paired = {}
    for site_name in profiles:
        for load_name in loads:
            for metric, lower_is_better in COMPARISON_METRICS:
                comparator = np.asarray([
                    getattr(row, metric)
                    for row in rows
                    if row.site == site_name and row.load_state == load_name and row.policy == "static_periodic"
                ])
                candidate = np.asarray([
                    getattr(row, metric)
                    for row in rows
                    if row.site == site_name and row.load_state == load_name and row.policy == "triageloop"
                ])
                paired[f"{site_name}|{load_name}|{metric}"] = _bootstrap_relative(
                    comparator,
                    candidate,
                    lower_is_better=lower_is_better,
                    seed=base_seed + 1_000_000 + len(paired),
                )

    surge_periodic = [row for row in rows if row.load_state == "surge_3x" and row.policy == "static_periodic"]
    surge_triage = [row for row in rows if row.load_state == "surge_3x" and row.policy == "triageloop"]
    overall_surge = {}
    for metric, lower_is_better in COMPARISON_METRICS[:4]:
        overall_surge[metric] = _bootstrap_relative(
            np.asarray([getattr(row, metric) for row in surge_periodic]),
            np.asarray([getattr(row, metric) for row in surge_triage]),
            lower_is_better=lower_is_better,
            seed=base_seed + 1_100_000 + len(overall_surge),
        )

    response_sensitivity = {}
    for response_allowance in (10, 20, 30):
        adjusted_templates = _templates_with_response_allowance(templates, response_allowance)
        periodic_misses = []
        triageloop_misses = []
        for site_index, profile in enumerate(profiles.values()):
            for repetition in range(30):
                seed = base_seed + 1_200_000 + response_allowance * 1_000 + site_index * 100 + repetition
                tasks, triage_utilization = create_shift(
                    profile,
                    loads["surge_3x"],
                    shift_minutes,
                    adjusted_templates,
                    seed,
                )
                periodic_misses.append(
                    simulate_shift(
                        tasks,
                        profile,
                        shift_minutes,
                        "surge_3x",
                        "static_periodic",
                        seed,
                        triage_utilization,
                    ).action_window_miss_rate
                )
                triageloop_misses.append(
                    simulate_shift(
                        tasks,
                        profile,
                        shift_minutes,
                        "surge_3x",
                        "triageloop",
                        seed,
                        triage_utilization,
                    ).action_window_miss_rate
                )
        comparison = _bootstrap_relative(
            np.asarray(periodic_misses),
            np.asarray(triageloop_misses),
            lower_is_better=True,
            seed=base_seed + 1_300_000 + response_allowance,
        )
        response_sensitivity[str(response_allowance)] = {
            "periodic_retriage_mean": comparison.pop("static_mean"),
            **comparison,
            "paired_policy_shifts": len(periodic_misses) * 2,
        }

    evaluation_dir = root / "artifacts" / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    shift_path = evaluation_dir / "tl-05-periodic-retriage-shifts.jsonl"
    with shift_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(asdict(row), sort_keys=True) + "\n")
    results = {
        "verification_version": "1.0.0",
        "simulation_version": SIMULATION_VERSION,
        "base_seed": base_seed,
        "periodic_retriage_minutes": 15,
        "replications_per_cell": replications,
        "site_profiles": list(profiles),
        "load_states": loads,
        "policies": list(VERIFICATION_POLICIES),
        "total_policy_shifts": len(rows),
        "configuration_sha256": hashlib.sha256((root / "data" / "specs" / "site-profiles.json").read_bytes()).hexdigest(),
        "cells": cells,
        "paired_comparisons": paired,
        "overall_surge": overall_surge,
        "deterioration_response_sensitivity": response_sensitivity,
        "interpretation_gates": {
            "directionally_fewer_surge_misses_than_periodic_retriage": overall_surge["action_window_miss_rate"]["relative_improvement"] > 0,
            "low_acuity_p90_no_more_than_20pct_worse_than_periodic": overall_surge["low_acuity_p90_wait_minutes"]["triageloop_mean"] <= 1.20 * overall_surge["low_acuity_p90_wait_minutes"]["static_mean"],
            "all_cells_have_registered_replications": all(cell["replications"] == replications for cell in cells.values()),
        },
        "registered_gate_notice": "The original >=20% gate was registered against initial static triage, not this stronger TL-05 comparator. No new 20% threshold is retroactively imposed.",
        "sensitivity_notice": "The 10/20/30-minute periodic-comparator sensitivity is a TL-06.5 post-verification robustness analysis, not a retroactively registered gate.",
        "synthetic_simulation_only": True,
        "not_for_clinical_or_staffing_use": True,
    }
    (evaluation_dir / "tl-05-periodic-retriage-metrics.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results
