from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dataset import Dataset

router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_dataset(
    project_id: int,
    name: str,
    version: str = "1.0",
    file_path: str = "",
    db: Session = Depends(get_db),
):
    dataset = Dataset(
        project_id=project_id,
        name=name,
        version=version,
        file_path=file_path,
    )

    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return dataset


@router.get("/")
def list_datasets(
    db: Session = Depends(get_db),
):
    return db.scalars(select(Dataset)).all()


@router.get("/{dataset_id}")
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
):
    dataset = db.get(Dataset, dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    return dataset


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
):
    dataset = db.get(Dataset, dataset_id)

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    db.delete(dataset)
    db.commit()

    return {
        "message": "Dataset deleted successfully",
    }
