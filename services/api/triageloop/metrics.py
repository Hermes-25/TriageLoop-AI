"""Dependency-light binary prediction metrics."""

from __future__ import annotations

import numpy as np


def confusion(y: np.ndarray, p: np.ndarray, threshold: float) -> dict[str, int]:
    predicted = p >= threshold
    actual = y.astype(bool)
    return {
        "tp": int(np.sum(predicted & actual)),
        "fp": int(np.sum(predicted & ~actual)),
        "tn": int(np.sum(~predicted & ~actual)),
        "fn": int(np.sum(~predicted & actual)),
    }


def recall(y: np.ndarray, p: np.ndarray, threshold: float) -> float:
    counts = confusion(y, p, threshold)
    denominator = counts["tp"] + counts["fn"]
    return counts["tp"] / denominator if denominator else 1.0


def precision(y: np.ndarray, p: np.ndarray, threshold: float) -> float:
    counts = confusion(y, p, threshold)
    denominator = counts["tp"] + counts["fp"]
    return counts["tp"] / denominator if denominator else 1.0


def brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


def expected_calibration_error(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    total = len(y)
    result = 0.0
    for index in range(bins):
        lower, upper = edges[index], edges[index + 1]
        mask = (p >= lower) & (p < upper if index < bins - 1 else p <= upper)
        if np.any(mask):
            result += np.sum(mask) / total * abs(float(np.mean(y[mask])) - float(np.mean(p[mask])))
    return float(result)


def roc_auc(y: np.ndarray, p: np.ndarray) -> float:
    positives = int(np.sum(y == 1))
    negatives = int(np.sum(y == 0))
    if positives == 0 or negatives == 0:
        return 0.5
    order = np.argsort(p, kind="mergesort")
    sorted_p = p[order]
    ranks = np.empty(len(p), dtype=float)
    start = 0
    while start < len(p):
        end = start + 1
        while end < len(p) and sorted_p[end] == sorted_p[start]:
            end += 1
        ranks[order[start:end]] = (start + 1 + end) / 2
        start = end
    rank_sum = float(np.sum(ranks[y == 1]))
    return (rank_sum - positives * (positives + 1) / 2) / (positives * negatives)


def select_threshold(y: np.ndarray, p: np.ndarray, cost_ratio: float = 10, min_recall: float = 0.90) -> dict[str, float]:
    candidates = np.unique(np.concatenate((np.linspace(0.01, 0.99, 99), np.quantile(p, np.linspace(0, 1, 101)))))
    feasible = []
    all_options = []
    for threshold in candidates:
        counts = confusion(y, p, float(threshold))
        row_recall = recall(y, p, float(threshold))
        cost = cost_ratio * counts["fn"] + counts["fp"]
        row = (cost, -float(threshold), float(threshold), row_recall)
        all_options.append(row)
        if row_recall >= min_recall:
            feasible.append(row)
    selected = min(feasible or all_options)
    return {"threshold": selected[2], "recall": selected[3], "cost": float(selected[0]), "cost_ratio": cost_ratio}
