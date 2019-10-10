.PHONY: help

help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

clean: ## Clean local environment
	@rm -rf .pytest_cache
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf

dependencies: ## Install development dependencies
	pip install -U -r requirements-dev.txt

test: clean ## Run tests
	pytest -x

lint: ## Run code lint
	flake8 --show-source tests/ todists/ setup.py
