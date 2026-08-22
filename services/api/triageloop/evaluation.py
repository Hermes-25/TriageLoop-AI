"""TL-02 model fitting, comparison and evidence generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from .features import FeatureTransformer, HORIZONS, build_snapshot_dataset, feature_names, load_encounters
from .metrics import brier, expected_calibration_error, precision, recall, roc_auc, select_threshold
from .modeling import CalibratedModel, MultiHorizonModel
from .uncertainty import MondrianConformal, OODDetector


MODEL_VERSION = "2.0.0"


def _validation_masks(metadata: list[dict[str, object]]) -> tuple[np.ndarray, np.ndarray]:
    identifier = np.asarray([int(str(row["encounter_id"]).split("-")[-1]) for row in metadata])
    calibration = identifier % 2 == 0
    return calibration, ~calibration


def _metrics(labels: np.ndarray, probabilities: np.ndarray, thresholds: list[float]) -> dict[str, object]:
    result = {}
    for index, horizon in enumerate(HORIZONS):
        y, p, threshold = labels[:, index], probabilities[:, index], thresholds[index]
        result[str(horizon)] = {
            "prevalence": float(np.mean(y)),
            "threshold": threshold,
            "recall": recall(y, p, threshold),
            "precision": precision(y, p, threshold),
            "brier": brier(y, p),
            "ece": expected_calibration_error(y, p),
            "roc_auc": roc_auc(y, p),
            "review_rate": float(np.mean(p >= threshold)),
        }
    return result


def _subgroups(
    labels: np.ndarray,
    probabilities: np.ndarray,
    metadata: list[dict[str, object]],
    threshold: float,
    horizon_index: int = 2,
) -> dict[str, dict[str, float]]:
    output = {}
    dimensions = {
        "age_group": sorted({str(row["age_group"]) for row in metadata}),
        "history_status": sorted({str(row["history_status"]) for row in metadata}),
    }
    for dimension, groups in dimensions.items():
        for group in groups:
            mask = np.asarray([row[dimension] == group for row in metadata])
            y, p = labels[mask, horizon_index], probabilities[mask, horizon_index]
            output[f"{dimension}:{group}"] = {
                "n": int(np.sum(mask)),
                "prevalence": float(np.mean(y)),
                "recall": recall(y, p, threshold),
                "ece": expected_calibration_error(y, p),
            }
    return output


def _candidate(
    family: str,
    train: tuple[np.ndarray, np.ndarray, list[dict[str, object]]],
    validation: tuple[np.ndarray, np.ndarray, list[dict[str, object]]],
    test: tuple[np.ndarray, np.ndarray, list[dict[str, object]]],
    stress: tuple[np.ndarray, np.ndarray, list[dict[str, object]]],
    transformer: FeatureTransformer,
) -> tuple[dict[str, object], dict[str, object]]:
    x_train, y_train, _ = train
    x_validation, y_validation, meta_validation = validation
    x_test, y_test, meta_test = test
    x_stress, y_stress, meta_stress = stress
    tx_train = transformer.transform(x_train)
    tx_validation = transformer.transform(x_validation)
    tx_test = transformer.transform(x_test)
    tx_stress = transformer.transform(x_stress)
    probability_mask, operating_mask = _validation_masks(meta_validation)

    model = MultiHorizonModel(family=family).fit(tx_train, y_train)
    calibrated = CalibratedModel.fit(model, tx_validation[probability_mask], y_validation[probability_mask])
    p_operating = calibrated.predict_proba(tx_validation[operating_mask])
    thresholds = []
    operating_points = {}
    for index, horizon in enumerate(HORIZONS):
        operating_points[str(horizon)] = {
            str(cost): select_threshold(y_validation[operating_mask, index], p_operating[:, index], cost_ratio=cost)
            for cost in (5, 10, 20)
        }
        thresholds.append(operating_points[str(horizon)]["10"]["threshold"])

    conformal = MondrianConformal(alpha=0.10).fit(p_operating, y_validation[operating_mask])
    ood = OODDetector().fit(tx_train)
    p_test = calibrated.predict_proba(tx_test)
    p_stress = calibrated.predict_proba(tx_stress)
    conformal_test = {str(horizon): conformal.coverage(p_test, y_test, index) for index, horizon in enumerate(HORIZONS)}
    conformal_stress = {str(horizon): conformal.coverage(p_stress, y_stress, index) for index, horizon in enumerate(HORIZONS)}
    conformal_sweep = {}
    for alpha in (0.05, 0.10, 0.15):
        candidate_conformal = MondrianConformal(alpha=alpha).fit(p_operating, y_validation[operating_mask])
        conformal_sweep[str(alpha)] = {
            "test": {str(horizon): candidate_conformal.coverage(p_test, y_test, index) for index, horizon in enumerate(HORIZONS)},
            "stress": {str(horizon): candidate_conformal.coverage(p_stress, y_stress, index) for index, horizon in enumerate(HORIZONS)},
        }
    importance = model.feature_importance()
    ranked = np.argsort(importance)[::-1][:12]
    report = {
        "family": family,
        "validation_operating": _metrics(y_validation[operating_mask], p_operating, thresholds),
        "test": _metrics(y_test, p_test, thresholds),
        "stress": _metrics(y_stress, p_stress, thresholds),
        "operating_points": operating_points,
        "conformal": {"alpha": 0.10, "selection_basis": "locked 90% nominal class-conditional coverage; sweep retained for workload sensitivity", "test": conformal_test, "stress": conformal_stress, "sweep": conformal_sweep},
        "ood": {
            "threshold": ood.threshold,
            "test_rate": float(np.mean(ood.predict(tx_test))),
            "stress_rate": float(np.mean(ood.predict(tx_stress))),
        },
        "subgroups_30m": {
            "test": _subgroups(y_test, p_test, meta_test, thresholds[2]),
            "stress": _subgroups(y_stress, p_stress, meta_stress, thresholds[2]),
        },
        "top_features": [{"feature": feature_names()[i], "importance": float(importance[i])} for i in ranked],
    }
    artifact = {
        "model_version": MODEL_VERSION,
        "family": family,
        "transformer": transformer.to_dict(),
        "calibrated_model": calibrated.to_dict(),
        "thresholds": {str(horizon): thresholds[index] for index, horizon in enumerate(HORIZONS)},
        "conformal": conformal.to_dict(),
        "ood": ood.to_dict(),
        "feature_names": feature_names(),
        "synthetic_only": True,
        "not_for_clinical_use": True,
    }
    return report, artifact


def _selection(logistic: dict[str, object], boosted: dict[str, object]) -> dict[str, object]:
    def average(report: dict[str, object], split: str, metric: str) -> float:
        return float(np.mean([report[split][str(horizon)][metric] for horizon in HORIZONS]))

    logistic_test_recall = average(logistic, "test", "recall")
    boosted_test_recall = average(boosted, "test", "recall")
    logistic_stress_recall = average(logistic, "stress", "recall")
    boosted_stress_recall = average(boosted, "stress", "recall")
    logistic_test_brier = average(logistic, "test", "brier")
    boosted_test_brier = average(boosted, "test", "brier")
    def passes_safety_gates(report: dict[str, object]) -> bool:
        return all(
            report["test"][str(horizon)]["recall"] >= 0.90
            and report["stress"][str(horizon)]["recall"] >= 0.85
            and report["test"][str(horizon)]["ece"] <= 0.08
            and report["conformal"]["test"][str(horizon)]["critical"] >= 0.87
            and report["conformal"]["stress"][str(horizon)]["critical"] >= 0.87
            for horizon in HORIZONS
        )

    logistic_passes = passes_safety_gates(logistic)
    boosted_passes = passes_safety_gates(boosted)
    materially_better = (boosted_test_recall - logistic_test_recall >= 0.02) or (logistic_test_brier - boosted_test_brier >= 0.01)
    safe_tradeoff = boosted_stress_recall >= logistic_stress_recall - 0.02
    gate_override = boosted_passes and not logistic_passes
    selected = "boosted" if gate_override or (materially_better and safe_tradeoff) else "logistic"
    return {
        "selected": selected,
        "rule": "challenger wins if it passes all locked safety gates while the primary fails; otherwise it requires >=0.02 mean test-recall gain or >=0.01 mean Brier gain with stress recall no more than 0.02 worse",
        "safety_gate_pass": {"logistic": logistic_passes, "boosted": boosted_passes},
        "gate_override": gate_override,
        "materially_better": materially_better,
        "safe_tradeoff": safe_tradeoff,
        "comparison": {
            "test_mean_recall": {"logistic": logistic_test_recall, "boosted": boosted_test_recall},
            "stress_mean_recall": {"logistic": logistic_stress_recall, "boosted": boosted_stress_recall},
            "test_mean_brier": {"logistic": logistic_test_brier, "boosted": boosted_test_brier},
        },
    }


def run_evaluation(dataset_path: Path, artifact_root: Path) -> dict[str, object]:
    datasets = build_snapshot_dataset(load_encounters(dataset_path))
    transformer = FeatureTransformer.create().fit(datasets["train"][0])
    logistic_report, logistic_artifact = _candidate("logistic", **datasets, transformer=transformer)
    boosted_report, boosted_artifact = _candidate("boosted", **datasets, transformer=transformer)
    selection = _selection(logistic_report, boosted_report)
    selected_artifact = boosted_artifact if selection["selected"] == "boosted" else logistic_artifact

    model_dir = artifact_root / "models" / "tl-02"
    evaluation_dir = artifact_root / "evaluation"
    model_dir.mkdir(parents=True, exist_ok=True)
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "selected-model.json"
    model_path.write_text(json.dumps(selected_artifact, indent=2) + "\n", encoding="utf-8")
    checksum = hashlib.sha256(model_path.read_bytes()).hexdigest()
    results = {
        "model_version": MODEL_VERSION,
        "dataset": str(dataset_path),
        "snapshot_counts": {split: len(values[0]) for split, values in datasets.items()},
        "label_prevalence": {split: dict(zip(map(str, HORIZONS), values[1].mean(axis=0).tolist())) for split, values in datasets.items()},
        "candidates": {"logistic": logistic_report, "boosted": boosted_report},
        "selection": selection,
        "selected_model_sha256": checksum,
        "synthetic_only": True,
        "not_for_clinical_use": True,
    }
    (evaluation_dir / "tl-02-metrics.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (model_dir / "manifest.json").write_text(json.dumps({"model_version": MODEL_VERSION, "selected": selection["selected"], "sha256": checksum}, indent=2) + "\n", encoding="utf-8")
    return results
