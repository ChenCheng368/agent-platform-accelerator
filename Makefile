.PHONY: help setup-backend setup-frontend dev dev-backend dev-frontend build clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup-backend: ## Set up backend (Python venv + deps)
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	@echo "✓ Backend ready. Copy backend/.env.example to backend/.env and fill in credentials."

setup-frontend: ## Set up frontend (npm install)
	cd frontend && npm install

setup: setup-backend setup-frontend ## Set up both backend and frontend

dev-backend: ## Run backend dev server
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

dev-frontend: ## Run frontend dev server
	cd frontend && npm run dev

dev: ## Run both (use two terminals or docker-compose)
	@echo "Run in separate terminals:"
	@echo "  make dev-backend"
	@echo "  make dev-frontend"
	@echo ""
	@echo "Or use: docker-compose up"

build: ## Build production Docker image
	docker build -t agent-platform-accelerator .

clean: ## Clean generated files
	rm -rf backend/.venv backend/__pycache__
	rm -rf frontend/node_modules frontend/dist
