.PHONY: help install dev test clean docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  make install      - Install all dependencies"
	@echo "  make dev          - Start development servers"
	@echo "  make test         - Run all tests"
	@echo "  make clean        - Clean temporary files"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make migrate      - Run database migrations"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Done!"

dev:
	@echo "Starting development servers..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:5173"
	@make -j2 dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "All tests passed!"

test-coverage:
	@echo "Running tests with coverage..."
	cd backend && pytest --cov=app --cov-report=html --cov-report=term
	@echo "Coverage report generated in backend/htmlcov/"

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -delete 2>/dev/null || true
	@echo "Cleaned!"

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Containers started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "API Docs: http://localhost:8000/docs"

docker-up-postgres:
	@echo "Starting Docker containers with PostgreSQL..."
	docker-compose --profile postgres up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "Containers stopped!"

docker-logs:
	docker-compose logs -f

migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head
	@echo "Migrations complete!"

migrate-create:
	@read -p "Enter migration message: " msg; \
	cd backend && alembic revision --autogenerate -m "$$msg"

lint:
	@echo "Running linters..."
	cd backend && python -m pylint app/
	cd frontend && npm run lint

format:
	@echo "Formatting code..."
	cd backend && python -m black app/
	cd backend && python -m isort app/
	@echo "Code formatted!"

setup-env:
	@echo "Setting up environment files..."
	cp .env.example .env
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "Environment files created. Please edit them with your configuration."

db-shell:
	cd backend && python -c "from app.core.database import SessionLocal; db = SessionLocal(); print('Database shell ready. Use db variable.')"
