include .env
export

.PHONY: up down clean run run-gemini logs ps rebuild

up:
	docker compose up --build -d

upf:
	docker compose up --build

down:
	docker compose down --remove-orphans

clean:
	docker compose down --remove-orphans -v

rebuild:
	docker compose build --no-cache

EXP ?= gemini-flash
run:
	docker compose exec backend python scripts/run_evaluation.py --experiment "$(EXP)"

run-gemini:
	docker compose exec -e LLM_PROVIDER=gemini -e GEMINI_API_KEY=$(KEY) backend \
		python scripts/run_evaluation.py --experiment "$(EXP)"

run-gemini-auto:
	docker compose exec -e LLM_PROVIDER=gemini -e GEMINI_API_KEY=$${GEMINI_API_KEY} backend \
		python scripts/run_evaluation.py --experiment "$(EXP)"

logs:
	docker compose logs -f

ps:
	docker compose ps
