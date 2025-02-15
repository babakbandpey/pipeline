#!/bin/bash
# Fix SSH permissions
chmod 700 /root/.ssh
chmod 600 /root/.ssh/*

# Use SSH config if exists
if [ -f /root/.ssh/config ]; then
    chmod 600 /root/.ssh/config
fi

# Execute the main command
exec "$@"
