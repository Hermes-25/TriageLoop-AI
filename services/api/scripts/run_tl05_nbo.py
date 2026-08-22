from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services" / "api"))

from triageloop.nbo_evaluation import run_nbo_counterfactual


if __name__ == "__main__":
    result = run_nbo_counterfactual(ROOT)
    print({"eligible_snapshots": result["eligible_snapshots"], "comparison": result["comparison"], "gates": result["gates"]})
