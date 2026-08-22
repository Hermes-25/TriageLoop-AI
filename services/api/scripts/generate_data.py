"""Generate TL-01 data artifacts from the repository root."""

from pathlib import Path
import sys

service_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(service_root))

from triageloop.curated import write_curated_cases
from triageloop.generator import GeneratorConfig, write_dataset


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    manifest = write_dataset(root / "data" / "generated", GeneratorConfig())
    write_curated_cases(root / "data" / "fixtures" / "curated-cases.json")
    print(manifest)
