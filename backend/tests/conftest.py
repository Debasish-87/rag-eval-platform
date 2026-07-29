import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# These must be set before anything imports app.core.config, since
# Settings() is instantiated at module import time.
os.environ.setdefault("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'test_rag_eval.db'}")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("APP_NAME", "RAG Evaluation Platform (test)")
os.environ.setdefault("APP_VERSION", "test")
os.environ.setdefault("REPORTS_DIR", str(BACKEND_DIR / "test_reports"))

import pytest  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.database import SessionLocal, engine  # noqa: E402
from app.db.session import get_db  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _test_schema():
    """Create a clean schema once for the whole test session."""

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    db_file = BACKEND_DIR / "test_rag_eval.db"
    if db_file.exists():
        db_file.unlink()


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    def _override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def sample_dataset_path() -> str:
    return str(BACKEND_DIR / "app" / "datasets" / "sample_dataset.json")
