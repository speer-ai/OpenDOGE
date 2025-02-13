#!/bin/bash

# Exit on error
set -e

echo "Deploying OpenDOGE..."

# Check if running with sudo/root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Update system
echo "Updating system..."
apt-get update
apt-get upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p nginx/ssl nginx/conf.d nginx/logs

# Generate self-signed SSL certificate if not exists
if [ ! -f nginx/ssl/opendoge.crt ]; then
    echo "Generating SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/opendoge.key \
        -out nginx/ssl/opendoge.crt \
        -subj "/C=US/ST=State/L=City/O=OpenDOGE/CN=opendoge.local"
fi

# Build and start containers
echo "Building and starting containers..."
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "Checking services..."
if docker-compose ps | grep -q "Up"; then
    echo "OpenDOGE deployed successfully!"
    echo "Access the application at https://your-domain"
else
    echo "Deployment failed. Check logs with: docker-compose logs"
    exit 1
fi

# Print useful commands
echo "
Useful commands:
- View logs: docker-compose logs -f
- Restart services: docker-compose restart
- Stop services: docker-compose down
- Update and restart: ./scripts/deploy.sh
" 