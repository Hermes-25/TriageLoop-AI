from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services" / "api"))

from triageloop.verification_evaluation import run_periodic_retriage_experiment


if __name__ == "__main__":
    results = run_periodic_retriage_experiment(ROOT)
    print({"gates": results["interpretation_gates"], "overall_surge": results["overall_surge"]})
