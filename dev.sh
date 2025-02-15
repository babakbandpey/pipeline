#!/bin/bash
# Development setup script

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating .env from .env-demo..."
    cp .env-demo .env
    echo "Please update .env with your settings"
    exit 1
fi

# Generate SSH config if needed
if [ ! -f ~/.ssh/config ]; then
    echo "Generating SSH config..."
    mkdir -p ~/.ssh
    cat > ~/.ssh/config <<EOF
Host ${GIT_SSH_HOST_WORK}
    HostName github.com
    User git
    IdentityFile ${GIT_SSH_KEY_WORK}

Host ${GIT_SSH_HOST_PERSONAL}
    HostName github.com
    User git
    IdentityFile ${GIT_SSH_KEY_PERSONAL}
EOF
    chmod 600 ~/.ssh/config
fi

# Build and start containers
docker-compose up --build -d

# Install package in editable mode
docker-compose exec pipeline pip install -e .

# Configure Git inside container
docker-compose exec pipeline bash -c "
    git config --global user.name \"${GIT_AUTHOR_NAME}\" &&
    git config --global user.email \"${GIT_AUTHOR_EMAIL}\"
"

# Open shell
docker-compose exec pipeline fish
