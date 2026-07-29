from dataclasses import dataclass, field


@dataclass(slots=True)
class DatasetSample:
    """
    Represents a single RAG evaluation sample.
    """

    question: str

    contexts: list[str]

    answer: str

    ground_truth: str | None = None

    # Which of `contexts` are actually relevant to the question.
    # Used by retrieval metrics (Precision@K, Recall@K, MRR, MAP,
    # NDCG, HitRate). Defaults to empty (no retrieval credit) when
    # not provided by the dataset.
    relevant_contexts: list[str] = field(default_factory=list)

    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Dataset:
    """
    Collection of evaluation samples.
    """

    name: str

    samples: list[DatasetSample] = field(default_factory=list)

    metadata: dict[str, str] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.samples)

    def add(
        self,
        sample: DatasetSample,
    ) -> None:
        self.samples.append(sample)
