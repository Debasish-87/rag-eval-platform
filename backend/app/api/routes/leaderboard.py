from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.experiment import Experiment
from app.models.benchmark import Benchmark
from app.models.evaluation import Evaluation
from app.models.metric import Metric

router = APIRouter(
    prefix="/leaderboard",
    tags=["Leaderboard"],
)


@router.get("/")
def leaderboard(
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            Project.name.label("project"),
            Experiment.name.label("experiment"),
            Benchmark.id.label("benchmark_id"),
            Benchmark.name.label("benchmark"),
            Benchmark.status.label("status"),
            func.count(func.distinct(Evaluation.id)).label("evaluations"),
            func.avg(Metric.score).label("overall_score"),
        )
        .join(
            Experiment,
            Experiment.project_id == Project.id,
        )
        .join(
            Benchmark,
            Benchmark.experiment_id == Experiment.id,
        )
        .outerjoin(
            Evaluation,
            Evaluation.benchmark_id == Benchmark.id,
        )
        .outerjoin(
            Metric,
            Metric.evaluation_id == Evaluation.id,
        )
        .group_by(
            Project.name,
            Experiment.name,
            Benchmark.id,
            Benchmark.name,
            Benchmark.status,
        )
        .order_by(func.avg(Metric.score).desc().nullslast())
    )

    rows = db.execute(stmt).all()

    results = []

    for rank, row in enumerate(rows, start=1):
        results.append(
            {
                "rank": rank,
                "project": row.project,
                "experiment": row.experiment,
                "benchmark_id": row.benchmark_id,
                "benchmark": row.benchmark,
                "status": row.status,
                "evaluations": row.evaluations,
                "overall_score": (
                    round(float(row.overall_score), 4)
                    if row.overall_score is not None
                    else 0.0
                ),
            }
        )

    return results
