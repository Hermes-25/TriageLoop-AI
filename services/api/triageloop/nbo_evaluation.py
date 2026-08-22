"""Counterfactual Next Best Observation verification for TL-05."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

import numpy as np

from .features import event_minute, load_encounters
from .recommendation import ModelBundle, RecommendedAction, rank_observation_options, recommend
from .safety import evaluate_safety
from .schemas import Observation, ObservationSource, PatientState


FIXED_BUNDLE_SIZE = 8
MAX_MATERIAL_RECALL_LOSS = 0.02
ACTION_POSITIVE = {
    RecommendedAction.IMMEDIATE_REVIEW,
    RecommendedAction.REASSESS,
    RecommendedAction.ESCALATE_PRIORITY,
    RecommendedAction.SAFE_MODE_REVIEW,
}
CODE_TO_FIELDS = {
    "repeat_heart_rate": ("heart_rate_bpm",),
    "repeat_respiratory_rate": ("respiratory_rate_per_min",),
    "repeat_spo2": ("spo2_percent",),
    "repeat_blood_pressure": ("systolic_bp_mmhg", "diastolic_bp_mmhg"),
    "repeat_temperature": ("temperature_c",),
    "repeat_mental_status": ("gcs", "mental_status"),
    "repeat_pain": ("pain_score_0_10",),
}


def _targeted_patient(patient: PatientState, index: int, observation_codes: tuple[str, ...]) -> tuple[PatientState, bool]:
    current = patient.observations[index]
    future = patient.observations[index + 1]
    updates = {}
    available = False
    for observation_code in observation_codes:
        for field in CODE_TO_FIELDS.get(observation_code, ()):
            value = getattr(future.values, field)
            updates[field] = value
            available = available or value is not None
    values = current.values.model_copy(update=updates)
    acquired = Observation(
        observation_id=f"NBO-{current.observation_id}-{index}",
        recorded_at=future.recorded_at,
        source=ObservationSource.REASSESSMENT,
        values=values,
        quality=future.quality,
    )
    return patient.model_copy(update={"observations": [*patient.observations[: index + 1], acquired]}), available


def _recall(labels: list[bool], predictions: list[bool]) -> float:
    positives = sum(labels)
    if positives == 0:
        return 0.0
    return sum(label and prediction for label, prediction in zip(labels, predictions, strict=True)) / positives


def run_nbo_counterfactual(root: Path) -> dict[str, object]:
    bundle = ModelBundle.from_path(root / "artifacts" / "models" / "tl-02" / "selected-model.json")
    catalogue = json.loads((root / "data" / "specs" / "observation-catalogue.json").read_text(encoding="utf-8"))
    seconds = {item["code"]: int(item["typical_seconds"]) for item in catalogue["items"]}
    fixed_bundle_seconds = sum(seconds.values())
    rows = []
    for encounter in load_encounters(root / "data" / "generated" / "encounters.jsonl"):
        if encounter.truth.split not in {"test", "stress"}:
            continue
        patient = encounter.patient
        event = event_minute(encounter)
        for index in range(len(patient.observations) - 1):
            current_patient = patient.model_copy(update={"observations": patient.observations[: index + 1]})
            current_time = patient.observations[index].recorded_at
            base = recommend(current_patient, bundle, evaluated_at=current_time)
            if base.next_best_observation is None:
                continue
            next_time = patient.observations[index + 1].recorded_at
            full_patient = patient.model_copy(update={"observations": patient.observations[: index + 2]})
            full = recommend(full_patient, bundle, evaluated_at=next_time)
            safety = evaluate_safety(current_patient, evaluated_at=current_time)
            probability, _sets, _ood, _transformed = bundle.predict(current_patient)
            quality_fields = set(safety.data_quality.missing_fields + safety.data_quality.implausible_fields)
            ranked = rank_observation_options(
                current_patient,
                bundle,
                probability,
                base.action_window.maximum_minutes,
                quality_fields,
            )
            targeted_results = {}
            availability = {}
            for count in range(1, 7):
                codes = tuple(option.observation_code for option in ranked[:count])
                targeted_patient, available = _targeted_patient(patient, index, codes)
                targeted_results[count] = recommend(targeted_patient, bundle, evaluated_at=next_time)
                availability[count] = available
            targeted = targeted_results[1]
            elapsed = (current_time - patient.arrival_time).total_seconds() / 60
            label = bool(event is not None and event <= elapsed + 30)
            rows.append({
                "encounter_id": encounter.encounter_id,
                "split": encounter.truth.split,
                "age_group": "pediatric" if patient.age_years < 12 else "geriatric" if patient.age_years >= 65 else "adult",
                "history_status": patient.history_status.value,
                "observation_code": base.next_best_observation.observation_code,
                "observation_available": available,
                "label_critical_30m": label,
                "fixed_bundle_positive": full.recommended_action in ACTION_POSITIVE,
                "nbo_positive": targeted.recommended_action in ACTION_POSITIVE,
                "fixed_bundle_risk_positive": bool(full.risk_by_horizon["30"] >= bundle.thresholds[2]),
                "nbo_risk_positive": bool(targeted.risk_by_horizon["30"] >= bundle.thresholds[2]),
                "base_ambiguous": len(base.uncertainty.prediction_set) != 1,
                "fixed_bundle_ambiguous": len(full.uncertainty.prediction_set) != 1,
                "nbo_ambiguous": len(targeted.uncertainty.prediction_set) != 1,
                "fixed_bundle_action": full.recommended_action.value,
                "nbo_action": targeted.recommended_action.value,
                "nbo_expected_decision_value": base.next_best_observation.expected_decision_value,
                "nbo_seconds": seconds.get(base.next_best_observation.observation_code, 90),
                "adaptive": {
                    str(count): {
                        "observation_codes": [option.observation_code for option in ranked[:count]],
                        "typical_seconds": sum(seconds.get(option.observation_code, 90) for option in ranked[:count]),
                        "observation_available": availability[count],
                        "positive": targeted_results[count].recommended_action in ACTION_POSITIVE,
                        "risk_positive": bool(targeted_results[count].risk_by_horizon["30"] >= bundle.thresholds[2]),
                        "ambiguous": len(targeted_results[count].uncertainty.prediction_set) != 1,
                        "action": targeted_results[count].recommended_action.value,
                    }
                    for count in range(1, 7)
                },
            })

    labels = [bool(row["label_critical_30m"]) for row in rows]
    fixed_predictions = [bool(row["fixed_bundle_positive"]) for row in rows]
    nbo_predictions = [bool(row["nbo_positive"]) for row in rows]
    fixed_recall = _recall(labels, fixed_predictions)
    nbo_recall = _recall(labels, nbo_predictions)
    mean_nbo_seconds = float(np.mean([row["nbo_seconds"] for row in rows])) if rows else 0.0
    observation_reduction = 1 - (1 / FIXED_BUNDLE_SIZE)
    time_reduction = 1 - (mean_nbo_seconds / fixed_bundle_seconds) if fixed_bundle_seconds else 0.0

    subgroup = defaultdict(dict)
    for field in ("split", "age_group", "history_status"):
        for value in sorted({str(row[field]) for row in rows}):
            subset = [row for row in rows if row[field] == value]
            subset_labels = [bool(row["label_critical_30m"]) for row in subset]
            subgroup[field][value] = {
                "eligible_snapshots": len(subset),
                "critical_snapshots": sum(subset_labels),
                "fixed_bundle_operational_recall": _recall(subset_labels, [bool(row["fixed_bundle_positive"]) for row in subset]),
                "nbo_operational_recall": _recall(subset_labels, [bool(row["nbo_positive"]) for row in subset]),
            }

    fallback_sensitivity = {}
    for count in range(1, 7):
        item = {}
        for split in ("test", "stress", "combined"):
            subset = rows if split == "combined" else [row for row in rows if row["split"] == split]
            subset_labels = [bool(row["label_critical_30m"]) for row in subset]
            fixed_subset = [bool(row["fixed_bundle_positive"]) for row in subset]
            adaptive_subset = [bool(row["adaptive"][str(count)]["positive"]) for row in subset]
            fixed_subset_recall = _recall(subset_labels, fixed_subset)
            adaptive_recall = _recall(subset_labels, adaptive_subset)
            item[split] = {
                "fixed_bundle_operational_recall": fixed_subset_recall,
                "adaptive_operational_recall": adaptive_recall,
                "recall_difference_adaptive_minus_fixed": adaptive_recall - fixed_subset_recall,
                "observation_count_reduction": 1 - count / FIXED_BUNDLE_SIZE,
                "mean_typical_seconds": float(np.mean([row["adaptive"][str(count)]["typical_seconds"] for row in subset])) if subset else 0.0,
                "passes_recall_boundary": fixed_subset_recall - adaptive_recall <= MAX_MATERIAL_RECALL_LOSS,
            }
        fallback_sensitivity[str(count)] = item
    selected_count = next(
        (
            count
            for count in range(2, 7)
            if fallback_sensitivity[str(count)]["test"]["passes_recall_boundary"]
            and fallback_sensitivity[str(count)]["test"]["observation_count_reduction"] >= 0.25
        ),
        None,
    )
    fallback = {
        "selected_observation_count_on_test": selected_count,
        "selection_rule": "Smallest 2-6 observation bundle with >=25% count reduction and <=0.02 absolute operational recall loss on test.",
        "stress_confirmation_passed": bool(
            selected_count is not None
            and fallback_sensitivity[str(selected_count)]["stress"]["passes_recall_boundary"]
        ),
        "status": "qualified" if selected_count is not None and fallback_sensitivity[str(selected_count)]["stress"]["passes_recall_boundary"] else "not_qualified",
    }

    results = {
        "evaluation_version": "1.0.0",
        "eligible_snapshots": len(rows),
        "critical_snapshots": sum(labels),
        "fixed_bundle": {
            "observations_per_reassessment": FIXED_BUNDLE_SIZE,
            "typical_seconds": fixed_bundle_seconds,
            "operational_critical_recall": fixed_recall,
            "risk_threshold_critical_recall": _recall(labels, [bool(row["fixed_bundle_risk_positive"]) for row in rows]),
            "ambiguity_rate_after_acquisition": float(np.mean([row["fixed_bundle_ambiguous"] for row in rows])) if rows else 0.0,
        },
        "next_best_observation": {
            "observations_per_reassessment": 1,
            "mean_typical_seconds": mean_nbo_seconds,
            "operational_critical_recall": nbo_recall,
            "risk_threshold_critical_recall": _recall(labels, [bool(row["nbo_risk_positive"]) for row in rows]),
            "ambiguity_rate_after_acquisition": float(np.mean([row["nbo_ambiguous"] for row in rows])) if rows else 0.0,
            "unavailable_observation_rate": float(np.mean([not row["observation_available"] for row in rows])) if rows else 0.0,
            "action_agreement_with_fixed_bundle": float(np.mean([row["nbo_action"] == row["fixed_bundle_action"] for row in rows])) if rows else 0.0,
            "mean_expected_decision_value": float(np.mean([row["nbo_expected_decision_value"] for row in rows])) if rows else 0.0,
        },
        "comparison": {
            "observation_count_reduction": observation_reduction,
            "estimated_measurement_time_reduction": time_reduction,
            "operational_recall_difference_nbo_minus_fixed": nbo_recall - fixed_recall,
        },
        "fallback_sensitivity": fallback_sensitivity,
        "adaptive_bundle_fallback": fallback,
        "release_decision": {
            "status": "failed_safety_gate",
            "permitted_product_role": "first measurement suggestion only",
            "prohibited_claim": "NBO replaces full reassessment or preserves critical recall",
            "safe_fallback": "Complete the full reassessment bundle or escalate whenever the observation is unavailable, uncertainty persists, or clinical concern remains.",
        },
        "gates": {
            "at_least_25pct_fewer_observations": observation_reduction >= 0.25,
            "no_material_operational_recall_loss": fixed_recall - nbo_recall <= MAX_MATERIAL_RECALL_LOSS,
        },
        "material_recall_loss_definition": "No more than 0.02 absolute operational critical-recall loss versus the fixed eight-observation bundle; fixed before running this evaluation.",
        "subgroups": subgroup,
        "method_limitations": [
            "Synthetic longitudinal trajectories supply the counterfactual next measurement.",
            "The targeted path carries forward unrequested recent values and replaces only the selected measurement group.",
            "Typical acquisition times come from the prototype catalogue, not an observed nurse time-and-motion study.",
            "This evaluates decision efficiency within the synthetic system, not clinical effectiveness.",
            "The single-observation gate remains reported even if an adaptive multi-observation fallback qualifies.",
        ],
        "synthetic_evaluation_only": True,
    }
    evaluation_dir = root / "artifacts" / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    (evaluation_dir / "tl-05-nbo-metrics.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    with (evaluation_dir / "tl-05-nbo-cases.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return results
