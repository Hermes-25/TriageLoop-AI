"""Export canonical product snapshots for the Vercel UI presentation adapter."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "services" / "api"))

from triageloop.product_store import ProductStore  # noqa: E402


def snapshot(store: ProductStore) -> dict[str, object]:
    return {"state": store.state(), "audit": store.audit(limit=200)}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="triageloop-vercel-") as temp:
        store = ProductStore(Path(temp) / "demo.sqlite3")
        store.reset()
        baseline = snapshot(store)
        store.deteriorate("P-0009")
        baseline_deteriorated = snapshot(store)

        store.reset()
        store.set_scenario("surge_3x")
        surge = snapshot(store)
        store.deteriorate("P-0009")
        surge_deteriorated = snapshot(store)

        payload = {
            "schema_version": "1.0.0",
            "adapter_notice": "Canonical FastAPI snapshots for the public synthetic UI demonstration; local Docker remains the full-stack reference.",
            "states": {
                "baseline": baseline,
                "baseline_deteriorated": baseline_deteriorated,
                "surge_3x": surge,
                "surge_3x_deteriorated": surge_deteriorated,
            },
            "evaluation": store.evaluation(),
        }
        output = ROOT / "apps" / "web" / "app" / "lib" / "vercel-demo-fixtures.json"
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        print(output)


if __name__ == "__main__":
    main()
