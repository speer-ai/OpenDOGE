#!/bin/bash

# Exit on error
set -e

echo "Deploying OpenDOGE to DigitalOcean Droplet..."

# Check if running with sudo/root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Update system
echo "Updating system..."
apt-get update
apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
apt-get install -y \
    curl \
    git \
    ufw \
    certbot \
    python3-certbot-nginx

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

# Configure firewall
echo "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Create necessary directories
echo "Creating directories..."
mkdir -p nginx/ssl nginx/conf.d nginx/logs

# Generate self-signed SSL certificate if not exists and Let's Encrypt cert not present
if [ ! -f nginx/ssl/opendoge.crt ] && [ ! -f /etc/letsencrypt/live/*/fullchain.pem ]; then
    echo "Generating temporary SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/opendoge.key \
        -out nginx/ssl/opendoge.crt \
        -subj "/C=US/ST=State/L=City/O=OpenDOGE/CN=localhost"
fi

# Pull latest code if in a git repository
if [ -d .git ]; then
    echo "Pulling latest code..."
    git pull
fi

# Build and start containers
echo "Building and starting containers..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "Checking services..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "OpenDOGE deployed successfully!"
else
    echo "Deployment failed. Check logs with: docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi

# Print useful commands
echo "
Deployment completed! Here are some useful commands:

View logs:
  docker-compose -f docker-compose.prod.yml logs -f

Restart services:
  docker-compose -f docker-compose.prod.yml restart

Stop services:
  docker-compose -f docker-compose.prod.yml down

Update and restart:
  ./scripts/droplet_deploy.sh

To set up SSL with Let's Encrypt:
  certbot --nginx -d your-domain.com

Monitor containers:
  docker-compose -f docker-compose.prod.yml ps
" 