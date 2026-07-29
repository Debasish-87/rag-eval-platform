from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.benchmark import Benchmark

router = APIRouter(
    prefix="/benchmarks",
    tags=["Benchmarks"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_benchmark(
    experiment_id: int,
    name: str,
    db: Session = Depends(get_db),
):
    benchmark = Benchmark(
        experiment_id=experiment_id,
        name=name,
        status="pending",
    )

    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)

    return benchmark


@router.get("/")
def list_benchmarks(
    db: Session = Depends(get_db),
):
    return db.scalars(select(Benchmark)).all()


@router.get("/{benchmark_id}")
def get_benchmark(
    benchmark_id: int,
    db: Session = Depends(get_db),
):
    benchmark = db.get(Benchmark, benchmark_id)

    if benchmark is None:
        raise HTTPException(
            status_code=404,
            detail="Benchmark not found",
        )

    return benchmark


@router.patch("/{benchmark_id}/status")
def update_benchmark_status(
    benchmark_id: int,
    status_value: str,
    db: Session = Depends(get_db),
):
    benchmark = db.get(Benchmark, benchmark_id)

    if benchmark is None:
        raise HTTPException(
            status_code=404,
            detail="Benchmark not found",
        )

    benchmark.status = status_value

    db.commit()
    db.refresh(benchmark)

    return benchmark


@router.delete("/{benchmark_id}")
def delete_benchmark(
    benchmark_id: int,
    db: Session = Depends(get_db),
):
    benchmark = db.get(Benchmark, benchmark_id)

    if benchmark is None:
        raise HTTPException(
            status_code=404,
            detail="Benchmark not found",
        )

    db.delete(benchmark)
    db.commit()

    return {
        "message": "Benchmark deleted successfully",
    }
