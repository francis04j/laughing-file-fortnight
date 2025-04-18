# Makefile for setting up Python project with virtualenv and dependencies

# Python executable
PYTHON = python3

# Virtual environment directory
VENV_DIR = venv

# Requirements file
REQUIREMENTS = requirements.txt

.PHONY: help setup install freeze clean run

# Show available commands
help:
	@echo "Usage:"
	@echo "  make setup      - Create and activate virtual environment, install deps, and generate requirements.txt"
	@echo "  make install    - Install dependencies from requirements.txt"
	@echo "  make freeze     - Freeze installed packages to requirements.txt"
	@echo "  make clean      - Remove virtual environment"

# Create virtual environment, install packages, and freeze requirements
setup: $(VENV_DIR)/bin/activate
	@echo "Installing dependencies..."
	source $(VENV_DIR)/bin/activate && \
	pip install --upgrade pip && \
	pip install fastapi uvicorn boto3 python-multipart && \
	pip freeze > $(REQUIREMENTS)
	@echo "Setup complete."

# Create virtual environment if not exists
$(VENV_DIR)/bin/activate:
	@echo "Creating virtual environment in $(VENV_DIR)..."
	$(PYTHON) -m venv $(VENV_DIR)

# Install dependencies from requirements.txt
install:
	@echo "Activating virtualenv and installing from $(REQUIREMENTS)..."
	source $(VENV_DIR)/bin/activate && pip install -r $(REQUIREMENTS)

# Freeze current dependencies into requirements.txt
freeze:
	source $(VENV_DIR)/bin/activate && pip freeze > $(REQUIREMENTS)
	@echo "Dependencies frozen to $(REQUIREMENTS)"

# Remove virtual environment
clean:
	rm -rf $(VENV_DIR)
	@echo "Virtual environment removed."

run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload
