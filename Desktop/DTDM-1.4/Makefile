# Makefile for Scalable AI API System

.PHONY: help install test lint format clean validate

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies and setup development environment
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

test:  ## Run all tests
	python -m pytest tests/ -v

test-coverage:  ## Run tests with coverage report
	python -m pytest tests/ --cov=scalable_ai_api --cov-report=html --cov-report=term

lint:  ## Run code linting
	python -m mypy scalable_ai_api/
	python -m isort --check-only scalable_ai_api/ tests/
	python -m black --check scalable_ai_api/ tests/

format:  ## Format code
	python -m isort scalable_ai_api/ tests/
	python -m black scalable_ai_api/ tests/

validate:  ## Validate project setup
	python validate_setup.py

clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

dev-setup: install validate  ## Complete development setup
	@echo "Development environment setup complete!"

# Docker operations
docker-build:  ## Build Docker images
	@echo "Building Docker images..."
	docker build -f Dockerfile.loadbalancer -t scalable-ai-api-loadbalancer .
	docker build -f Dockerfile.aiserver -t scalable-ai-api-server .

docker-run:  ## Run with Docker Compose
	@echo "Starting services with Docker Compose..."
	docker-compose up -d
	@echo "Services started! Check status with: docker-compose ps"
	@echo "Load Balancer: http://localhost:8000"
	@echo "Server A: http://localhost:8080"
	@echo "Server B: http://localhost:8081"

docker-run-prod:  ## Run in production mode
	@echo "Starting services in production mode..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production services started!"

docker-stop:  ## Stop Docker services
	@echo "Stopping Docker services..."
	docker-compose down

docker-clean:  ## Clean Docker images and containers
	@echo "Cleaning Docker images and containers..."
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

docker-test:  ## Test Docker deployment
	@echo "Testing Docker deployment..."
	docker-compose up -d
	sleep 30
	curl -f http://localhost:8000/health || exit 1
	curl -f http://localhost:8080/health || exit 1
	curl -f http://localhost:8081/health || exit 1
	@echo "Docker deployment test passed!"
	docker-compose down

# Local development
run-local:  ## Run services locally (instructions)
	@echo "Starting services locally..."
	@echo "Run these commands in separate terminals:"
	@echo "Terminal 1: python server_a.py"
	@echo "Terminal 2: python server_b.py"
	@echo "Terminal 3: python -m uvicorn scalable_ai_api.load_balancer.render_app:app --host 0.0.0.0 --port 8000"

# Render deployment
render-prepare:  ## Prepare for Render deployment
	@echo "Preparing for Render deployment..."
	python -c "import scalable_ai_api; print('✓ Package imports work')"
	python -c "import scalable_ai_api.load_balancer.render_app; print('✓ Load balancer app imports work')"
	python -c "import scalable_ai_api.ai_server.render_app; print('✓ AI server app imports work')"
	@echo "✓ Ready for Render deployment!"