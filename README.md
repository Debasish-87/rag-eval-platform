# RAG Evaluation Platform

A production-ready platform for evaluating Retrieval-Augmented Generation (RAG) systems. The platform benchmarks retrieval quality, generation quality, and LLM-as-a-Judge metrics while providing experiment tracking, report generation, REST APIs, and a lightweight dashboard.

The project is built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, **Docker**, and a modular evaluation engine that makes it easy to add new metrics and evaluators.

---
![Dashboard](screenshots/Dashboard.png)
---
## Table of Contents

- Overview
- Features
- Architecture
- Evaluation Workflow
- Project Structure
- Technology Stack
- Installation
- Docker Deployment
- API Endpoints
- Evaluation Metrics
- Reports
- Screenshots
- Testing
- Future Improvements
- License

---

# Features

## Evaluation

- Retrieval evaluation
- Generation evaluation
- LLM-as-a-Judge evaluation
- Batch evaluation support
- Benchmark execution
- Experiment management

## Retrieval Metrics

- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Mean Average Precision (MAP)
- Normalized Discounted Cumulative Gain (NDCG)
- Hit Rate

## Generation Metrics

- Faithfulness
- Correctness
- Semantic Similarity

## LLM Judge

- Faithfulness
- Answer Relevance
- Hallucination Detection

## Reports

- JSON
- CSV
- Markdown

## Dashboard

- Leaderboard
- Benchmark comparison
- Metric visualization
- Report downloads

---

# System Architecture

```text
                              +----------------------+
                              |     Frontend UI      |
                              | HTML • CSS • JS      |
                              +----------+-----------+
                                         |
                                         |
                                  REST API Calls
                                         |
                                         ▼
                         +-------------------------------+
                         |           FastAPI             |
                         |      API & Route Layer        |
                         +---------------+---------------+
                                         |
          +------------------------------+------------------------------+
          |                              |                              |
          ▼                              ▼                              ▼
  Project Manager                Experiment Manager             Report Service
          |                              |                              |
          +------------------------------+------------------------------+
                                         |
                                         ▼
                              Evaluation Engine
                                         |
               +-------------------------+--------------------------+
               |                         |                          |
               ▼                         ▼                          ▼
     Retrieval Evaluator      Generation Evaluator        LLM Judge Evaluator
               |                         |                          |
               +------------+------------+--------------------------+
                            |
                            ▼
                     Metric Runner
                            |
        +-------------------+-----------------------------+
        |                   |              |              |
        ▼                   ▼              ▼              ▼
  Retrieval Metrics   Generation     LLM Metrics    Hallucination
                      Metrics
                            |
                            ▼
                     Database Layer
                    PostgreSQL / SQLite
                            |
                            ▼
                     Report Generator
                            |
             JSON • CSV • Markdown Reports
                            |
                            ▼
                     Dashboard & API
```

---

# Evaluation Workflow

```text
                Load Dataset
                     │
                     ▼
            Validate Dataset
                     │
                     ▼
      Convert to Evaluation Requests
                     │
                     ▼
            Evaluation Engine
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
 Retrieval     Generation      LLM Judge
 Evaluation    Evaluation      Evaluation
       │             │             │
       └─────────────┼─────────────┘
                     │
                     ▼
          Aggregate Metric Scores
                     │
                     ▼
          Store Benchmark Results
                     │
                     ▼
          Generate Reports
       (JSON / CSV / Markdown)
                     │
                     ▼
         Dashboard & Leaderboard
```

---

# Request Lifecycle

```text
Client
   │
   ▼
FastAPI Endpoint
   │
   ▼
Dataset Loader
   │
   ▼
Evaluation Engine
   │
   ▼
Metric Runner
   │
   ▼
Database
   │
   ▼
Reports
   │
   ▼
Dashboard
```
---

# Project Structure

```
rag-eval-platform/
│
├── backend/
│   ├── app/
│   │   ├── api/                 # REST API routes
│   │   ├── core/                # Application configuration
│   │   ├── datasets/            # Dataset loader & validator
│   │   ├── db/                  # Database connection
│   │   ├── evaluation/          # Evaluation engine
│   │   ├── evaluators/          # Retrieval, Generation, LLM Judge
│   │   ├── experiments/         # Benchmark execution
│   │   ├── llm/                 # LLM providers
│   │   ├── metrics/             # Evaluation metrics
│   │   ├── models/              # SQLAlchemy models
│   │   ├── reports/             # JSON, CSV & Markdown reports
│   │   └── main.py              # FastAPI application
│   │
│   ├── migrations/              # Alembic migrations
│   ├── scripts/                 # Benchmark runner
│   ├── tests/                   # Unit & Integration tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── screenshots/
├── docker-compose.yml
└── README.md
```

---

# Technology Stack

| Category | Technology |
|----------|------------|
| Backend | FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Database | PostgreSQL, SQLite |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Validation | Pydantic |
| Testing | Pytest |
| Containerization | Docker |
| Report Format | JSON, CSV, Markdown |

---

# Installation

## Clone Repository

```bash
git clone <repository-url>

cd rag-eval-platform
```

---

## Backend Setup

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file inside the `backend` directory.

```env
DATABASE_URL=postgresql://raguser:ragpassword@localhost:5432/rag_eval

LLM_PROVIDER=mock

GEMINI_API_KEY=

GEMINI_MODEL=gemini-flash-latest

REPORTS_DIR=reports

DEBUG=False
```

---

## Run Database Migration

```bash
alembic upgrade head
```

---

## Run Evaluation Pipeline

```bash
python scripts/run_evaluation.py
```

---

## Start Backend

```bash
uvicorn app.main:app --reload
```

Backend API

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

---

## Start Frontend

```bash
cd frontend

python -m http.server 5500
```

Dashboard

```
http://localhost:5500
```

---

# Docker Deployment

Run the complete application.

```bash
docker compose up --build
```

Run in background.

```bash
docker compose up -d
```

Stop containers.

```bash
docker compose down
```

Remove volumes.

```bash
docker compose down -v
```

---

# Docker Architecture

```text
                 Docker Compose
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
 PostgreSQL      FastAPI Backend     Frontend
 Container          Container        Container
        │               │                │
        └───────────────┼────────────────┘
                        │
                 Docker Network
```

---

# Environment Variables

| Variable | Description |
|-----------|-------------|
| DATABASE_URL | Database connection string |
| LLM_PROVIDER | LLM provider (mock or gemini) |
| GEMINI_API_KEY | Gemini API key |
| GEMINI_MODEL | Gemini model name |
| REPORTS_DIR | Output directory for reports |
| DEBUG | Enable debug mode |
| CORS_ORIGINS | Allowed frontend origins |
| SEED_ON_START | Run benchmark during startup |

---

# Application Ports

| Service | Port |
|----------|------|
| Frontend | 5500 |
| Backend API | 8000 |
| PostgreSQL | 5432 |

---

# Production Deployment Checklist

- Configure environment variables
- Use PostgreSQL instead of SQLite
- Disable debug mode
- Secure API keys
- Enable HTTPS
- Configure reverse proxy (Nginx)
- Enable logging and monitoring
- Schedule database backups
- Configure Docker restart policies
- Run automated tests before deployment

---

# REST API

The platform exposes RESTful APIs for managing projects, datasets, experiments, benchmarks, reports, and evaluation summaries.

## Base URL

```
http://localhost:8000
```

---

## API Documentation

| Endpoint | Description |
|----------|-------------|
| `/docs` | Swagger UI |
| `/redoc` | ReDoc Documentation |

---

## Core Endpoints

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List projects |
| POST | `/projects` | Create project |
| GET | `/projects/{id}` | Get project |
| PUT | `/projects/{id}` | Update project |
| DELETE | `/projects/{id}` | Delete project |

---

### Datasets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/datasets` | List datasets |
| POST | `/datasets` | Upload dataset |
| GET | `/datasets/{id}` | Dataset details |

---

### Experiments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/experiments` | List experiments |
| POST | `/experiments` | Create experiment |
| GET | `/experiments/{id}` | Experiment details |

---

### Benchmarks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/benchmarks` | Benchmark history |
| POST | `/benchmarks/run` | Execute benchmark |
| GET | `/benchmarks/{id}` | Benchmark details |

---

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/json/{id}` | Download JSON report |
| GET | `/reports/csv/{id}` | Download CSV report |
| GET | `/reports/md/{id}` | Download Markdown report |

---

# Database Schema

```text
Projects
    │
    ├──────────────┐
    ▼              ▼
Datasets      Experiments
                     │
                     ▼
               Benchmarks
                     │
                     ▼
               Evaluations
                     │
                     ▼
                  Metrics
```

---

# Evaluation Metrics

## Retrieval Metrics

| Metric | Description |
|---------|-------------|
| Precision@K | Relevant retrieved documents |
| Recall@K | Coverage of relevant documents |
| MRR | Reciprocal rank of first relevant result |
| MAP | Mean Average Precision |
| NDCG | Ranking quality |
| Hit Rate | Whether at least one relevant document is retrieved |

---

## Generation Metrics

| Metric | Description |
|---------|-------------|
| Faithfulness | Answer supported by retrieved context |
| Correctness | Similarity to ground truth |
| Semantic Similarity | Embedding similarity between answer and reference |

---

## LLM-as-a-Judge

| Metric | Description |
|---------|-------------|
| Faithfulness | LLM verifies contextual grounding |
| Answer Relevance | Measures relevance to the question |
| Hallucination | Detects unsupported information |

---

# Report Generation

After every benchmark execution, the platform automatically generates reports.

Supported formats:

```
reports/

├── report.json
├── report.csv
└── report.md
```

The reports include:

- Overall benchmark summary
- Individual metric scores
- Average metric values
- Benchmark metadata
- Failed evaluation details
- Execution time

---

---

# Screenshots

## Dashboard

Overview dashboard showing projects, datasets, experiments, leaderboard, and benchmark statistics.

![Dashboard](screenshots/Dashboard.png)

---

## Benchmark Results

Detailed benchmark metrics, score breakdown, and evaluation summary.

![Benchmark Results](screenshots/dashboard_result.png)

---

## Generated Reports

Automatically generated benchmark reports in JSON, CSV, and Markdown formats.

![Reports](screenshots/report_result.png)

---

## Docker Deployment

Running the complete platform using Docker Compose with Backend, Frontend, and PostgreSQL services.

![Docker](screenshots/docker.png)

---

## Test Execution

Pytest execution showing successful unit and integration tests.

![Tests](screenshots/test_run_result.png)

---

# Testing

Run all tests.

```bash
pytest
```

Run with verbose output.

```bash
pytest -v
```

Run specific test.

```bash
pytest tests/test_api.py
```

---

# Future Improvements

- User authentication and authorization
- Multi-user collaboration
- Role-based access control (RBAC)
- Background task processing
- Redis caching
- Kubernetes deployment
- CI/CD pipeline
- Vector database integration
- Additional LLM providers (OpenAI, Claude, Azure OpenAI)
- Real-time evaluation monitoring
- WebSocket support
- Export reports as PDF and Excel
- Cloud storage integration
- Multi-project dashboard

---

# Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/new-feature
```

3. Commit your changes.

```bash
git commit -m "Add new feature"
```

4. Push the branch.

```bash
git push origin feature/new-feature
```

5. Open a Pull Request.

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for complete license information.