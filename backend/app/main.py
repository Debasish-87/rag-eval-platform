from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.benchmarks import router as benchmark_router
from app.api.routes.datasets import router as dataset_router
from app.api.routes.experiments import router as experiment_router
from app.api.routes.leaderboard import router as leaderboard_router
from app.api.routes.projects import router as project_router
from app.api.routes.reports import router as report_router
from app.api.routes.summary import router as summary_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# Allow the static dashboard (served from a different origin/port,
# e.g. http://localhost:5500) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(project_router)
app.include_router(dataset_router)
app.include_router(experiment_router)
app.include_router(benchmark_router)
app.include_router(report_router)
app.include_router(leaderboard_router)
app.include_router(summary_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
    }
