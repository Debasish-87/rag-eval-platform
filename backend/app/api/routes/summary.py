from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.benchmark import Benchmark
from app.models.dataset import Dataset
from app.models.evaluation import Evaluation
from app.models.experiment import Experiment
from app.models.metric import Metric
from app.models.project import Project

router = APIRouter(
    tags=["Summary"],
)


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
):
    """
    Aggregate counts and headline metrics for the dashboard's
    top-level overview cards.
    """

    projects = db.scalar(select(func.count(Project.id)))
    datasets = db.scalar(select(func.count(Dataset.id)))
    experiments = db.scalar(select(func.count(Experiment.id)))
    benchmarks = db.scalar(select(func.count(Benchmark.id)))
    evaluations = db.scalar(select(func.count(Evaluation.id)))
    average_score = db.scalar(select(func.avg(Metric.score)))

    metric_rows = db.execute(
        select(
            Metric.name,
            func.avg(Metric.score).label("avg_score"),
            func.count(Metric.id).label("count"),
        ).group_by(Metric.name)
    ).all()

    metric_averages = {row.name: round(float(row.avg_score), 4) for row in metric_rows}

    latest_benchmark = db.scalar(select(Benchmark).order_by(Benchmark.id.desc()))

    return {
        "projects": projects or 0,
        "datasets": datasets or 0,
        "experiments": experiments or 0,
        "benchmarks": benchmarks or 0,
        "evaluations": evaluations or 0,
        "average_score": (
            round(float(average_score), 4) if average_score is not None else 0.0
        ),
        "metric_averages": metric_averages,
        "latest_benchmark": (
            {
                "id": latest_benchmark.id,
                "name": latest_benchmark.name,
                "status": latest_benchmark.status,
                "completed_at": (
                    latest_benchmark.completed_at.isoformat()
                    if latest_benchmark.completed_at
                    else None
                ),
            }
            if latest_benchmark is not None
            else None
        ),
    }


@router.get("/benchmarks/{benchmark_id}/metrics")
def benchmark_metrics(
    benchmark_id: int,
    db: Session = Depends(get_db),
):
    """
    Per-metric averages for a single benchmark run, used to
    render retrieval/generation breakdowns and run comparisons.
    """

    benchmark = db.get(Benchmark, benchmark_id)

    if benchmark is None:
        raise HTTPException(
            status_code=404,
            detail="Benchmark not found",
        )

    rows = db.execute(
        select(
            Metric.name,
            func.avg(Metric.score).label("avg_score"),
            func.count(Metric.id).label("count"),
        )
        .join(Evaluation, Evaluation.id == Metric.evaluation_id)
        .where(Evaluation.benchmark_id == benchmark_id)
        .group_by(Metric.name)
    ).all()

    evaluation_count = db.scalar(
        select(func.count(Evaluation.id)).where(Evaluation.benchmark_id == benchmark_id)
    )

    return {
        "benchmark_id": benchmark.id,
        "benchmark_name": benchmark.name,
        "status": benchmark.status,
        "evaluations": evaluation_count or 0,
        "metrics": {row.name: round(float(row.avg_score), 4) for row in rows},
    }


@router.get("/benchmarks/{benchmark_id}/evaluations")
def benchmark_evaluations(
    benchmark_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """
    Per-sample evaluations with their metric scores, for the
    dashboard's drill-down table.
    """

    benchmark = db.get(Benchmark, benchmark_id)

    if benchmark is None:
        raise HTTPException(
            status_code=404,
            detail="Benchmark not found",
        )

    evaluations = db.scalars(
        select(Evaluation)
        .where(Evaluation.benchmark_id == benchmark_id)
        .order_by(Evaluation.id)
        .limit(limit)
    ).all()

    results = []

    for evaluation in evaluations:
        metrics = db.scalars(
            select(Metric).where(Metric.evaluation_id == evaluation.id)
        ).all()

        results.append(
            {
                "id": evaluation.id,
                "query": evaluation.query,
                "answer": evaluation.answer,
                "ground_truth": evaluation.ground_truth,
                "metrics": {metric.name: round(metric.score, 4) for metric in metrics},
            }
        )

    return results
