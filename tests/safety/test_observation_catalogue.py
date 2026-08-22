import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ObservationCatalogueTests(unittest.TestCase):
    def test_catalogue_is_bounded_and_low_burden(self) -> None:
        payload = json.loads((ROOT / "data" / "specs" / "observation-catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["items"]), 8)
        self.assertTrue(all(item["burden"] == "low" for item in payload["items"]))
        codes = " ".join(item["code"] for item in payload["items"])
        self.assertNotIn("medication", codes)
        self.assertNotIn("imaging", codes)


if __name__ == "__main__":
    unittest.main()
