"""Run the registered TL-03 Queue Twin matrix."""

from pathlib import Path
import sys

service_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(service_root))

from triageloop.queue_evaluation import run_queue_experiments


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    results = run_queue_experiments(root)
    print({"gates": results["gates"], "overall_surge": results["overall_surge"]})
