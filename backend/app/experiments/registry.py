from app.experiments.experiment import (
    ExperimentManager,
)


class ExperimentRegistry:
    """
    In-memory registry for active experiments.
    """

    _experiments: dict[
        str,
        ExperimentManager,
    ] = {}

    @classmethod
    def register(
        cls,
        manager: ExperimentManager,
    ) -> None:
        """
        Register an experiment manager.
        """

        cls._experiments[manager.experiment.experiment_id] = manager

    @classmethod
    def get(
        cls,
        experiment_id: str,
    ) -> ExperimentManager | None:
        """
        Retrieve an experiment by its ID.
        """

        return cls._experiments.get(experiment_id)

    @classmethod
    def list(
        cls,
    ) -> list[ExperimentManager]:
        """
        Return all registered experiments.
        """

        return list(cls._experiments.values())

    @classmethod
    def unregister(
        cls,
        experiment_id: str,
    ) -> None:
        """
        Remove an experiment from the registry.
        """

        cls._experiments.pop(
            experiment_id,
            None,
        )

    @classmethod
    def clear(cls) -> None:
        """
        Remove all registered experiments.
        """

        cls._experiments.clear()
