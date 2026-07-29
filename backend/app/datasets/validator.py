from app.datasets.exceptions import DatasetValidationError
from app.datasets.models import Dataset


class DatasetValidator:
    """
    Validates Dataset objects before they are used
    for benchmarking or evaluation.
    """

    @staticmethod
    def validate(dataset: Dataset) -> None:
        """
        Validate an entire dataset.

        Raises:
            DatasetValidationError:
                If any validation rule fails.
        """

        if dataset is None:
            raise DatasetValidationError("Dataset cannot be None.")

        if not dataset.name.strip():
            raise DatasetValidationError("Dataset name cannot be empty.")

        if not dataset.samples:
            raise DatasetValidationError("Dataset contains no samples.")

        seen_questions: set[str] = set()

        for index, sample in enumerate(
            dataset.samples,
            start=1,
        ):

            # -----------------------------
            # Question
            # -----------------------------
            if not isinstance(sample.question, str):
                raise DatasetValidationError(
                    f"Sample #{index}: question must be a string."
                )

            if not sample.question.strip():
                raise DatasetValidationError(
                    f"Sample #{index}: question cannot be empty."
                )

            # -----------------------------
            # Duplicate Questions
            # -----------------------------
            normalized_question = sample.question.strip().lower()

            if normalized_question in seen_questions:
                raise DatasetValidationError(
                    f"Sample #{index}: duplicate question " f"'{sample.question}'."
                )

            seen_questions.add(normalized_question)

            # -----------------------------
            # Contexts
            # -----------------------------
            if not isinstance(sample.contexts, list):
                raise DatasetValidationError(
                    f"Sample #{index}: contexts must be a list."
                )

            if len(sample.contexts) == 0:
                raise DatasetValidationError(
                    f"Sample #{index}: contexts cannot be empty."
                )

            for context_index, context in enumerate(
                sample.contexts,
                start=1,
            ):

                if not isinstance(context, str):
                    raise DatasetValidationError(
                        f"Sample #{index}: "
                        f"context #{context_index} "
                        f"must be a string."
                    )

                if not context.strip():
                    raise DatasetValidationError(
                        f"Sample #{index}: "
                        f"context #{context_index} "
                        f"cannot be empty."
                    )

            # -----------------------------
            # Answer
            # -----------------------------
            if not isinstance(sample.answer, str):
                raise DatasetValidationError(
                    f"Sample #{index}: answer must be a string."
                )

            if not sample.answer.strip():
                raise DatasetValidationError(
                    f"Sample #{index}: answer cannot be empty."
                )

            # -----------------------------
            # Ground Truth
            # -----------------------------
            if sample.ground_truth is not None and not isinstance(
                sample.ground_truth,
                str,
            ):
                raise DatasetValidationError(
                    f"Sample #{index}: " "ground_truth must be a string " "or None."
                )

            if isinstance(sample.ground_truth, str) and not sample.ground_truth.strip():
                raise DatasetValidationError(
                    f"Sample #{index}: " "ground_truth cannot be empty."
                )

            # -----------------------------
            # Metadata
            # -----------------------------
            if not isinstance(sample.metadata, dict):
                raise DatasetValidationError(
                    f"Sample #{index}: " "metadata must be a dictionary."
                )
