"""Interpretable and boosted multi-horizon models implemented with NumPy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from .features import HORIZONS


def sigmoid(raw: np.ndarray) -> np.ndarray:
    raw = np.clip(raw, -35, 35)
    return 1 / (1 + np.exp(-raw))


class BinaryEstimator(Protocol):
    def fit(self, x: np.ndarray, y: np.ndarray) -> "BinaryEstimator": ...
    def decision_function(self, x: np.ndarray) -> np.ndarray: ...
    def to_dict(self) -> dict[str, object]: ...


@dataclass
class LogisticHazard:
    l2: float = 0.1
    positive_weight: float = 5.0
    max_iter: int = 40
    tolerance: float = 1e-7
    weights: np.ndarray | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "LogisticHazard":
        design = np.column_stack((np.ones(len(x)), x))
        coefficients = np.zeros(design.shape[1])
        sample_weight = np.where(y == 1, self.positive_weight, 1.0)
        regularization = np.eye(design.shape[1]) * self.l2
        regularization[0, 0] = 0
        for _ in range(self.max_iter):
            probability = sigmoid(design @ coefficients)
            curvature = sample_weight * probability * (1 - probability)
            gradient = design.T @ (sample_weight * (probability - y)) + regularization @ coefficients
            hessian = (design.T * curvature) @ design + regularization + np.eye(design.shape[1]) * 1e-8
            step = np.linalg.solve(hessian, gradient)
            coefficients -= step
            if float(np.max(np.abs(step))) < self.tolerance:
                break
        self.weights = coefficients
        return self

    def decision_function(self, x: np.ndarray) -> np.ndarray:
        if self.weights is None:
            raise RuntimeError("model is not fitted")
        return self.weights[0] + x @ self.weights[1:]

    def feature_importance(self) -> np.ndarray:
        if self.weights is None:
            raise RuntimeError("model is not fitted")
        return np.abs(self.weights[1:])

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "logistic_hazard",
            "l2": self.l2,
            "positive_weight": self.positive_weight,
            "weights": self.weights.tolist(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "LogisticHazard":
        model = cls(l2=float(payload["l2"]), positive_weight=float(payload["positive_weight"]))
        model.weights = np.asarray(payload["weights"], dtype=float)
        return model


@dataclass
class DecisionStump:
    feature: int
    threshold: float
    left_value: float
    right_value: float
    gain: float

    def to_dict(self) -> dict[str, float | int]:
        return {
            "feature": self.feature,
            "threshold": self.threshold,
            "left_value": self.left_value,
            "right_value": self.right_value,
            "gain": self.gain,
        }


@dataclass
class BoostedHazard:
    estimators: int = 28
    learning_rate: float = 0.12
    l2: float = 2.0
    positive_weight: float = 5.0
    quantiles: int = 9
    initial_score: float = 0.0
    trees: list[DecisionStump] = field(default_factory=list)
    feature_count: int = 0

    def fit(self, x: np.ndarray, y: np.ndarray) -> "BoostedHazard":
        self.feature_count = x.shape[1]
        sample_weight = np.where(y == 1, self.positive_weight, 1.0)
        weighted_rate = float(np.sum(sample_weight * y) / np.sum(sample_weight))
        weighted_rate = min(1 - 1e-5, max(1e-5, weighted_rate))
        self.initial_score = float(np.log(weighted_rate / (1 - weighted_rate)))
        raw = np.full(len(y), self.initial_score)
        thresholds = [
            np.unique(np.quantile(x[:, feature], np.linspace(0.1, 0.9, self.quantiles)))
            for feature in range(x.shape[1])
        ]
        self.trees = []
        for _ in range(self.estimators):
            probability = sigmoid(raw)
            gradient = sample_weight * (y - probability)
            hessian = sample_weight * probability * (1 - probability)
            total_gradient = float(np.sum(gradient))
            total_hessian = float(np.sum(hessian))
            parent_gain = total_gradient**2 / (total_hessian + self.l2)
            best: DecisionStump | None = None
            for feature in range(x.shape[1]):
                column = x[:, feature]
                for threshold in thresholds[feature]:
                    left = column <= threshold
                    if np.all(left) or not np.any(left):
                        continue
                    g_left = float(np.sum(gradient[left]))
                    h_left = float(np.sum(hessian[left]))
                    g_right = total_gradient - g_left
                    h_right = total_hessian - h_left
                    gain = 0.5 * (g_left**2 / (h_left + self.l2) + g_right**2 / (h_right + self.l2) - parent_gain)
                    if best is None or gain > best.gain:
                        best = DecisionStump(
                            feature=feature,
                            threshold=float(threshold),
                            left_value=g_left / (h_left + self.l2),
                            right_value=g_right / (h_right + self.l2),
                            gain=gain,
                        )
            if best is None or best.gain <= 0:
                break
            self.trees.append(best)
            raw += self.learning_rate * np.where(x[:, best.feature] <= best.threshold, best.left_value, best.right_value)
        return self

    def decision_function(self, x: np.ndarray) -> np.ndarray:
        raw = np.full(len(x), self.initial_score)
        for tree in self.trees:
            raw += self.learning_rate * np.where(x[:, tree.feature] <= tree.threshold, tree.left_value, tree.right_value)
        return raw

    def feature_importance(self) -> np.ndarray:
        importance = np.zeros(self.feature_count)
        for tree in self.trees:
            importance[tree.feature] += max(0, tree.gain)
        total = float(np.sum(importance))
        return importance / total if total else importance

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "boosted_hazard",
            "estimators": self.estimators,
            "learning_rate": self.learning_rate,
            "l2": self.l2,
            "positive_weight": self.positive_weight,
            "quantiles": self.quantiles,
            "initial_score": self.initial_score,
            "feature_count": self.feature_count,
            "trees": [tree.to_dict() for tree in self.trees],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "BoostedHazard":
        model = cls(
            estimators=int(payload["estimators"]),
            learning_rate=float(payload["learning_rate"]),
            l2=float(payload["l2"]),
            positive_weight=float(payload["positive_weight"]),
            quantiles=int(payload["quantiles"]),
        )
        model.initial_score = float(payload["initial_score"])
        model.feature_count = int(payload["feature_count"])
        model.trees = [DecisionStump(**tree) for tree in payload["trees"]]
        return model


@dataclass
class MultiHorizonModel:
    family: str
    models: list[LogisticHazard | BoostedHazard] = field(default_factory=list)

    def fit(self, x: np.ndarray, y: np.ndarray) -> "MultiHorizonModel":
        self.models = []
        for index, _horizon in enumerate(HORIZONS):
            model: LogisticHazard | BoostedHazard
            model = LogisticHazard() if self.family == "logistic" else BoostedHazard()
            self.models.append(model.fit(x, y[:, index]))
        return self

    def decision_function(self, x: np.ndarray) -> np.ndarray:
        return np.column_stack([model.decision_function(x) for model in self.models])

    def feature_importance(self) -> np.ndarray:
        return np.mean(np.vstack([model.feature_importance() for model in self.models]), axis=0)

    def to_dict(self) -> dict[str, object]:
        return {"family": self.family, "horizons": list(HORIZONS), "models": [model.to_dict() for model in self.models]}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "MultiHorizonModel":
        result = cls(family=str(payload["family"]))
        result.models = [
            LogisticHazard.from_dict(model) if model["kind"] == "logistic_hazard" else BoostedHazard.from_dict(model)
            for model in payload["models"]
        ]
        return result


@dataclass
class PlattCalibrator:
    coefficients: np.ndarray | None = None

    def fit(self, raw_scores: np.ndarray, labels: np.ndarray) -> "PlattCalibrator":
        design = np.column_stack((np.ones(len(raw_scores)), raw_scores))
        coefficients = np.asarray([0.0, 1.0])
        regularization = np.diag([1e-6, 1e-3])
        for _ in range(50):
            probability = sigmoid(design @ coefficients)
            gradient = design.T @ (probability - labels) + regularization @ coefficients
            curvature = probability * (1 - probability)
            hessian = (design.T * curvature) @ design + regularization
            step = np.linalg.solve(hessian, gradient)
            coefficients -= step
            if float(np.max(np.abs(step))) < 1e-8:
                break
        self.coefficients = coefficients
        return self

    def predict(self, raw_scores: np.ndarray) -> np.ndarray:
        if self.coefficients is None:
            raise RuntimeError("calibrator is not fitted")
        return sigmoid(self.coefficients[0] + self.coefficients[1] * raw_scores)

    def to_dict(self) -> dict[str, object]:
        return {"coefficients": self.coefficients.tolist()}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "PlattCalibrator":
        return cls(coefficients=np.asarray(payload["coefficients"], dtype=float))


@dataclass
class CalibratedModel:
    model: MultiHorizonModel
    calibrators: list[PlattCalibrator]

    @classmethod
    def fit(cls, model: MultiHorizonModel, x_calibration: np.ndarray, y_calibration: np.ndarray) -> "CalibratedModel":
        raw = model.decision_function(x_calibration)
        calibrators = [PlattCalibrator().fit(raw[:, index], y_calibration[:, index]) for index in range(len(HORIZONS))]
        return cls(model=model, calibrators=calibrators)

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        raw = self.model.decision_function(x)
        probability = np.column_stack([self.calibrators[index].predict(raw[:, index]) for index in range(len(HORIZONS))])
        return np.maximum.accumulate(probability, axis=1)

    def to_dict(self) -> dict[str, object]:
        return {"model": self.model.to_dict(), "calibrators": [item.to_dict() for item in self.calibrators]}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "CalibratedModel":
        return cls(
            model=MultiHorizonModel.from_dict(payload["model"]),
            calibrators=[PlattCalibrator.from_dict(item) for item in payload["calibrators"]],
        )
