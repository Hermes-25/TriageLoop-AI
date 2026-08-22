"""Bounded input-distribution plausibility check using the open MIMIC-IV demo."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np

from .features import load_encounters
from .quality import PLAUSIBLE_RANGES


ITEM_MAP = {
    "220045": ("heart_rate_bpm", lambda value: value),
    "220210": ("respiratory_rate_per_min", lambda value: value),
    "224690": ("respiratory_rate_per_min", lambda value: value),
    "220277": ("spo2_percent", lambda value: value),
    "220179": ("systolic_bp_mmhg", lambda value: value),
    "220180": ("diastolic_bp_mmhg", lambda value: value),
    "223762": ("temperature_c", lambda value: value),
    "223761": ("temperature_c", lambda value: (value - 32) * 5 / 9),
    "226755": ("gcs", lambda value: value),
    "227013": ("gcs", lambda value: value),
}


def _summary(values: list[float]) -> dict[str, float | int]:
    array = np.asarray(values, dtype=float)
    return {
        "count": len(values),
        "minimum": float(np.min(array)),
        "p01": float(np.quantile(array, 0.01)),
        "median": float(np.median(array)),
        "p99": float(np.quantile(array, 0.99)),
        "maximum": float(np.max(array)),
    }


def run_external_plausibility(root: Path) -> dict[str, object]:
    external_root = root / "data" / "external" / "mimic-iv-demo-2.2"
    chart_path = external_root / "icu" / "chartevents.csv.gz"
    items_path = external_root / "icu" / "d_items.csv.gz"
    if not chart_path.exists() or not items_path.exists():
        raise FileNotFoundError("MIMIC-IV demo chartevents and d_items files are required")

    external: dict[str, list[float]] = {field: [] for field in set(field for field, _ in ITEM_MAP.values())}
    with gzip.open(chart_path, "rt", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            mapping = ITEM_MAP.get(row["itemid"])
            if mapping is None or not row.get("valuenum"):
                continue
            field, converter = mapping
            try:
                external[field].append(float(converter(float(row["valuenum"]))))
            except ValueError:
                continue

    synthetic: dict[str, list[float]] = {field: [] for field in external}
    for encounter in load_encounters(root / "data" / "generated" / "encounters.jsonl"):
        for observation in encounter.patient.observations:
            for field in synthetic:
                value = getattr(observation.values, field)
                if value is not None:
                    synthetic[field].append(float(value))

    fields = {}
    for field in sorted(external):
        if not external[field] or not synthetic[field]:
            continue
        external_summary = _summary(external[field])
        synthetic_summary = _summary(synthetic[field])
        lower, upper = PLAUSIBLE_RANGES[field]
        accepted = sum(lower <= value <= upper for value in external[field]) / len(external[field])
        fields[field] = {
            "mimic_demo": external_summary,
            "synthetic": synthetic_summary,
            "external_within_prototype_hard_range": accepted,
            "external_median_within_synthetic_p01_p99": synthetic_summary["p01"] <= external_summary["median"] <= synthetic_summary["p99"],
        }

    core_fields = {"heart_rate_bpm", "respiratory_rate_per_min", "spo2_percent", "systolic_bp_mmhg", "temperature_c"}
    results = {
        "evaluation_version": "1.0.0",
        "source": {
            "name": "MIMIC-IV Clinical Database Demo",
            "version": "2.2",
            "doi": "10.13026/dp1f-ex47",
            "url": "https://physionet.org/content/mimic-iv-demo/2.2/",
            "population": "Open 100-patient deidentified hospital/ICU demo; not an emergency-department cohort.",
            "chartevents_sha256": hashlib.sha256(chart_path.read_bytes()).hexdigest(),
            "d_items_sha256": hashlib.sha256(items_path.read_bytes()).hexdigest(),
        },
        "fields": fields,
        "coverage": {
            "mapped_fields": len(fields),
            "mapped_core_fields": len(core_fields.intersection(fields)),
            "external_measurements": sum(int(item["mimic_demo"]["count"]) for item in fields.values()),
        },
        "plausibility_checks": {
            "all_five_core_vital_fields_present": core_fields.issubset(fields),
            "at_least_95pct_within_hard_ranges_each_field": all(item["external_within_prototype_hard_range"] >= 0.95 for item in fields.values()),
            "all_external_medians_inside_synthetic_p01_p99": all(item["external_median_within_synthetic_p01_p99"] for item in fields.values()),
        },
        "interpretation": "This checks whether the synthetic input scale is grossly disconnected from an open real-world reference. It does not evaluate ED labels, calibration, deterioration prediction, Action Windows, queue outcomes or clinical validity.",
        "limitations": [
            "The open demo is a small adult hospital/ICU subset, not MIMIC-IV-ED.",
            "Repeated chart measurements are not independent patient observations.",
            "No model-performance metric is computed on this source.",
            "Paediatric and emergency-department transfer remain untested externally.",
        ],
        "externally_sourced_deidentified_data": True,
        "not_clinical_validation": True,
    }
    output = root / "artifacts" / "evaluation" / "tl-05-external-plausibility.json"
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return results
