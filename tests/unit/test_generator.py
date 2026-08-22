from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from triageloop.generator import GeneratorConfig, generate_dataset, write_dataset


class GeneratorTests(unittest.TestCase):
    def test_reproducible_for_same_seed(self) -> None:
        config = GeneratorConfig(seed=7, total_encounters=50, stress_encounters=5)
        first = [item.model_dump_json() for item in generate_dataset(config)]
        second = [item.model_dump_json() for item in generate_dataset(config)]
        self.assertEqual(first, second)

    def test_different_seed_changes_population(self) -> None:
        a = generate_dataset(GeneratorConfig(seed=7, total_encounters=20, stress_encounters=2))[0]
        b = generate_dataset(GeneratorConfig(seed=8, total_encounters=20, stress_encounters=2))[0]
        self.assertNotEqual(a.model_dump_json(), b.model_dump_json())

    def test_base_split_and_separate_stress_set(self) -> None:
        data = generate_dataset(GeneratorConfig(total_encounters=100, stress_encounters=10))
        counts = Counter(item.truth.split for item in data)
        self.assertEqual(counts, {"train": 54, "validation": 18, "test": 18, "stress": 10})

    def test_manifest_and_jsonl_are_written(self) -> None:
        with TemporaryDirectory() as tmp:
            manifest = write_dataset(Path(tmp), GeneratorConfig(total_encounters=30, stress_encounters=3))
            self.assertEqual(manifest["encounters"], 30)
            with (Path(tmp) / "encounters.jsonl").open(encoding="utf-8") as handle:
                self.assertEqual(sum(1 for _ in handle), 30)

    def test_population_includes_all_age_and_history_groups(self) -> None:
        data = generate_dataset(GeneratorConfig(total_encounters=500, stress_encounters=25))
        ages = {"pediatric" if item.patient.age_years < 12 else "geriatric" if item.patient.age_years >= 65 else "adult" for item in data}
        histories = {item.patient.history_status.value for item in data}
        self.assertEqual(ages, {"pediatric", "adult", "geriatric"})
        self.assertEqual(histories, {"none", "partial", "available"})


if __name__ == "__main__":
    unittest.main()
