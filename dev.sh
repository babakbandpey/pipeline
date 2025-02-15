#!/bin/bash
# Development setup script

# Build and start containers
docker-compose up --build -d

# Install package in editable mode
docker-compose exec pipeline pip install -e .

# Open shell
docker-compose exec pipeline fish
