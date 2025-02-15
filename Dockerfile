# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git \
    curl gnupg2 \
    build-essential \
    python3-dev \
    fish \
    pylint

# Create a Python virtual environment
RUN python3 -m venv /app/env

# Install pip requirements
COPY requirements.txt .
RUN /app/env/bin/pip install --upgrade pip && \
    /app/env/bin/pip install -r requirements.txt && \
    /app/env/bin/pip install python-dotenv cryptography

# Set environment variables
ENV VIRTUAL_ENV=/app/env
ENV PATH="/app/env/bin:$PATH"

# Set fish as default shell
SHELL ["/usr/bin/fish", "--command"]
CMD ["fish"]

# Set up git
RUN apt-get install -y git && \
    git config --global --add safe.directory /app

# Fix SSH permissions when container starts
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
