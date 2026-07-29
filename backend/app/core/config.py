from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RAG Evaluation Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    # Defaults to a local SQLite file so the platform can be demoed with
    # zero external services. Point DATABASE_URL at Postgres (see
    # docker-compose.yml) for a production-style deployment.
    DATABASE_URL: str = "sqlite:///./rag_eval.db"

    # LLM
    # "mock" runs a deterministic, offline heuristic judge so the full
    # pipeline works without any API key. Set LLM_PROVIDER=gemini and
    # provide GEMINI_API_KEY to use a real LLM-as-judge.
    LLM_PROVIDER: str = "mock"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"

    # Number of evaluation requests sent in a single LLM call.
    LLM_BATCH_SIZE: int = 10

    # CORS - comma separated list of allowed origins, "*" for all.
    CORS_ORIGINS: str = "*"

    # Reports
    REPORTS_DIR: str = "reports"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]

        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


settings = Settings()
