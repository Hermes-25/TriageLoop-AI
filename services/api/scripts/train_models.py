"""Train and evaluate TL-02 candidates from the repository root."""

from pathlib import Path
import sys

service_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(service_root))

from triageloop.evaluation import run_evaluation


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    results = run_evaluation(root / "data" / "generated" / "encounters.jsonl", root / "artifacts")
    print({"selection": results["selection"], "snapshot_counts": results["snapshot_counts"]})
