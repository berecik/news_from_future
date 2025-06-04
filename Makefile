.PHONY: help install run test test-cov lint format clean dev build setup wildcards freeze update fetch-news generate-example openapi docs redoc

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
POETRY = poetry
DOCS_DIR = docs
OPENAPI_JSON = $(DOCS_DIR)/openapi.json

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make install    - Install dependencies using Poetry"
	@echo "  make run        - Run the FastAPI application"
	@echo "  make dev        - Run the application in development mode with hot reload"
	@echo "  make test       - Run tests"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code with black and isort"
	@echo "  make clean      - Remove build artifacts and cache directories"
	@echo "  make wildcards  - Convert dependencies to wildcard versions (^x.y.z)"
	@echo "  make freeze     - Freeze dependencies to their installed versions (==x.y.z)"
	@echo "  make update     - Update dependencies after changing versions"
	@echo "  make fetch-news - Fetch latest news data"
	@echo "  make generate-example - Generate example future news"
	@echo "  make openapi    - Generate OpenAPI JSON schema"
	@echo "  make docs       - Serve Swagger UI documentation"
	@echo "  make redoc      - Serve ReDoc documentation"

setup:
	python -m pip install --upgrade pip
	pip install poetry
	poetry config virtualenvs.in-project true
	$(MAKE) install

install:
	$(POETRY) install

run:
	$(POETRY) run uvicorn main:app --host 0.0.0.0 --port 8000

dev:
	$(POETRY) run uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	$(POETRY) run pytest

test-cov:
	$(POETRY) run pytest --cov=app --cov-report=term-missing --cov-report=xml

lint:
	$(POETRY) run flake8 app tests
	$(POETRY) run black --check app tests
	$(POETRY) run isort --check app tests
	$(POETRY) run pyflakes .

format:
	$(POETRY) run black app tests
	$(POETRY) run isort app tests

clean:
	@echo "Cleaning project..."
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf tests/__pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	@echo "Project cleaned."

# Update dependencies after changing versions
update:
	@echo "Updating dependencies..."
	poetry lock --no-update

# Freeze dependencies to specific versions
deps-freeze:
	python scripts/manage_deps.py freeze
	@echo "Run 'poetry update' to ensure dependencies match the frozen versions"

# Set dependencies to wildcard versions
deps-wild:
	python scripts/manage_deps.py wildcard
	@echo "Run 'poetry update' to ensure you have the latest versions"

upgrade: deps-wild update
    poetry upgrade
    deps-freeze:
    @echo "Run  to ensure you have the latest versions"

ollama:
    @echo "Chose large language model from available in Ollama..."
    poetry run python scripts/set_ollama_model.py