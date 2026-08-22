"""Mondrian conformal prediction sets and feature-space shift checks."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _conservative_quantile(scores: np.ndarray, alpha: float) -> float:
    if len(scores) == 0:
        return 1.0
    rank = min(len(scores), int(np.ceil((len(scores) + 1) * (1 - alpha))))
    return float(np.sort(scores)[rank - 1])


@dataclass
class MondrianConformal:
    alpha: float = 0.10
    thresholds: list[dict[str, float]] | None = None

    def fit(self, probabilities: np.ndarray, labels: np.ndarray) -> "MondrianConformal":
        self.thresholds = []
        for horizon in range(probabilities.shape[1]):
            p = probabilities[:, horizon]
            y = labels[:, horizon]
            negative_scores = p[y == 0]
            positive_scores = 1 - p[y == 1]
            self.thresholds.append(
                {
                    "non_critical": _conservative_quantile(negative_scores, self.alpha),
                    "critical": _conservative_quantile(positive_scores, self.alpha),
                }
            )
        return self

    def prediction_sets(self, probabilities: np.ndarray) -> list[list[list[str]]]:
        if self.thresholds is None:
            raise RuntimeError("conformal predictor is not fitted")
        rows = []
        for probability_row in probabilities:
            horizon_sets = []
            for index, probability in enumerate(probability_row):
                labels = []
                if probability <= self.thresholds[index]["non_critical"]:
                    labels.append("non_critical")
                if 1 - probability <= self.thresholds[index]["critical"]:
                    labels.append("critical")
                horizon_sets.append(labels)
            rows.append(horizon_sets)
        return rows

    def coverage(self, probabilities: np.ndarray, labels: np.ndarray, horizon_index: int) -> dict[str, float]:
        sets = self.prediction_sets(probabilities)
        result = {}
        for target, name in ((0, "non_critical"), (1, "critical")):
            mask = labels[:, horizon_index] == target
            present = [name in sets[row][horizon_index] for row in range(len(sets)) if mask[row]]
            result[name] = float(np.mean(present)) if present else 1.0
        result["mean_set_size"] = float(np.mean([len(row[horizon_index]) for row in sets]))
        result["review_rate"] = float(np.mean([len(row[horizon_index]) != 1 for row in sets]))
        return result

    def to_dict(self) -> dict[str, object]:
        return {"alpha": self.alpha, "thresholds": self.thresholds}


@dataclass
class OODDetector:
    quantile: float = 0.99
    threshold: float | None = None

    def score(self, transformed_x: np.ndarray) -> np.ndarray:
        return np.mean(np.square(np.clip(transformed_x, -10, 10)), axis=1)

    def fit(self, transformed_x: np.ndarray) -> "OODDetector":
        self.threshold = float(np.quantile(self.score(transformed_x), self.quantile))
        return self

    def predict(self, transformed_x: np.ndarray) -> np.ndarray:
        if self.threshold is None:
            raise RuntimeError("OOD detector is not fitted")
        return self.score(transformed_x) > self.threshold

    def to_dict(self) -> dict[str, float]:
        return {"quantile": self.quantile, "threshold": self.threshold}
