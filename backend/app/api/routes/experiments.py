from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.experiment import Experiment

router = APIRouter(
    prefix="/experiments",
    tags=["Experiments"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_experiment(
    project_id: int,
    name: str,
    description: str | None = None,
    db: Session = Depends(get_db),
):
    experiment = Experiment(
        project_id=project_id,
        name=name,
        description=description,
    )

    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    return experiment


@router.get("/")
def list_experiments(
    db: Session = Depends(get_db),
):
    return db.scalars(select(Experiment)).all()


@router.get("/{experiment_id}")
def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
):
    experiment = db.get(Experiment, experiment_id)

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found",
        )

    return experiment


@router.delete("/{experiment_id}")
def delete_experiment(
    experiment_id: int,
    db: Session = Depends(get_db),
):
    experiment = db.get(Experiment, experiment_id)

    if experiment is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment not found",
        )

    db.delete(experiment)
    db.commit()

    return {
        "message": "Experiment deleted successfully",
    }
