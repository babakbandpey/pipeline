# Remove Docker
sudo apt-get remove --purge docker-ce docker-ce-cli containerd.io

# Update package list and install prerequisites
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Start Docker and enable it to start at boot
sudo systemctl start docker
sudo systemctl enable docker

# Verify Docker installation
docker --version

# Add current user to Docker group
sudo usermod -aG docker $USER

# Log out and log back in, or restart your system

# Verify Docker service status
sudo systemctl status docker

# Check Docker configuration files
sudo cat /etc/docker/daemon.json
sudo cat /lib/systemd/system/docker.service

# Run Docker Compose
# docker-compose up
