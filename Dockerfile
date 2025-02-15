# Use an official Python runtime as a parent image
FROM python:slim

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

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install python-dotenv cryptography

# Set fish as default shell
SHELL ["/usr/bin/fish", "--command"]

# Set up git with proper permissions
RUN git config --system --add safe.directory '*' && \
    git config --system --add safe.directory /app

# Fix SSH permissions when container starts
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["fish"]
