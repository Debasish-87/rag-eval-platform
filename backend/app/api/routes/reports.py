from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def _serve_report(benchmark_id: int, extension: str, media_type: str):
    path = Path(f"reports/benchmark_{benchmark_id}.{extension}")

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return FileResponse(
        path=path,
        filename=path.name,
        media_type=media_type,
    )


@router.get("/{benchmark_id}/json")
def json_report(benchmark_id: int):
    return _serve_report(benchmark_id, "json", "application/json")


@router.get("/{benchmark_id}/csv")
def csv_report(benchmark_id: int):
    return _serve_report(benchmark_id, "csv", "text/csv")


@router.get("/{benchmark_id}/markdown")
def markdown_report(benchmark_id: int):
    return _serve_report(benchmark_id, "md", "text/markdown")
