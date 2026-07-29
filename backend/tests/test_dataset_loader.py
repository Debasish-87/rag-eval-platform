import pytest

from app.datasets.exceptions import DatasetValidationError
from app.datasets.loader import DatasetLoader
from app.datasets.models import Dataset, DatasetSample
from app.datasets.validator import DatasetValidator


def test_load_sample_dataset(sample_dataset_path):
    dataset = DatasetLoader.load(sample_dataset_path)

    assert dataset.name == "sample_dataset"
    assert len(dataset) > 0
    assert all(sample.question for sample in dataset.samples)


def test_load_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        DatasetLoader.load("does/not/exist.json")


def test_load_non_json_raises(tmp_path):
    bad_file = tmp_path / "dataset.txt"
    bad_file.write_text("not json")

    with pytest.raises(ValueError):
        DatasetLoader.load(bad_file)


def test_valid_dataset_passes_validation(sample_dataset_path):
    dataset = DatasetLoader.load(sample_dataset_path)
    DatasetValidator.validate(dataset)  # should not raise


def test_validator_rejects_empty_dataset():
    with pytest.raises(DatasetValidationError):
        DatasetValidator.validate(Dataset(name="empty"))


def test_validator_rejects_duplicate_questions():
    dataset = Dataset(
        name="dupes",
        samples=[
            DatasetSample(
                question="Same question?",
                contexts=["A fact."],
                answer="An answer.",
            ),
            DatasetSample(
                question="Same question?",
                contexts=["A fact."],
                answer="Another answer.",
            ),
        ],
    )

    with pytest.raises(DatasetValidationError):
        DatasetValidator.validate(dataset)


def test_validator_rejects_empty_contexts():
    dataset = Dataset(
        name="no-contexts",
        samples=[
            DatasetSample(question="Q?", contexts=[], answer="A."),
        ],
    )

    with pytest.raises(DatasetValidationError):
        DatasetValidator.validate(dataset)
