#!/bin/bash
set -e

echo "======================================"
echo " RAG Evaluation Platform Demo"
echo "======================================"

echo "[1/3] Running the full evaluation pipeline..."
python scripts/run_evaluation.py

echo ""
echo "[2/3] Leaderboard"
curl -s http://127.0.0.1:8000/leaderboard/ | python3 -m json.tool || echo "(start the API with: uvicorn app.main:app --reload  --to see this live)"

echo ""
echo "[3/3] Done. Open:"
echo "  API docs:  http://localhost:8000/docs"
echo "  Dashboard: http://localhost:5500  (cd frontend && python3 -m http.server 5500)"
