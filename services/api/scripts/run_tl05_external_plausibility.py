from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services" / "api"))

from triageloop.external_plausibility import run_external_plausibility


if __name__ == "__main__":
    result = run_external_plausibility(ROOT)
    print({"coverage": result["coverage"], "plausibility_checks": result["plausibility_checks"]})
