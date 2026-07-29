import json
from pathlib import Path

from app.datasets.models import Dataset, DatasetSample


class DatasetLoader:
    """
    Loads evaluation datasets from disk.
    """

    @staticmethod
    def load(path: str | Path) -> Dataset:
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(path)

        if path.suffix.lower() != ".json":
            raise ValueError(f"Unsupported dataset format: {path.suffix}")

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        samples = [
            DatasetSample(
                question=item["question"],
                contexts=item["contexts"],
                answer=item["answer"],
                ground_truth=item.get("ground_truth"),
                relevant_contexts=item.get("relevant_contexts", []),
                metadata=item.get("metadata", {}),
            )
            for item in data
        ]

        return Dataset(
            name=path.stem,
            samples=samples,
        )
