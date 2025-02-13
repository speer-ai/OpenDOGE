#!/bin/bash

# Exit on error
set -e

# Configuration
DOMAIN="opendoge.us"
REPO_URL="https://github.com/speer-ai/OpenDOGE.git"
APP_DIR="/opt/opendoge"
EMAIL="nick@example.com"  # For SSL certificate

echo "Starting OpenDOGE setup on Ubuntu..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    redis-server \
    ufw

# Configure firewall
echo "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Install Docker and Docker Compose
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

echo "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create app directory and clone repository
echo "Cloning repository..."
mkdir -p $APP_DIR
git clone $REPO_URL $APP_DIR
cd $APP_DIR

# Create .env file
echo "Creating environment file..."
cat > .env << EOL
ENVIRONMENT=production
DEBUG=false
POSTGRES_USER=opendoge
POSTGRES_PASSWORD=$(openssl rand -hex 32)
POSTGRES_DB=opendoge
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql+asyncpg://opendoge:${POSTGRES_PASSWORD}@postgres:5432/opendoge
EOL

# Set up SSL certificate
echo "Setting up SSL certificate..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect

# Configure Nginx
echo "Configuring Nginx..."
cat > /etc/nginx/sites-available/opendoge << EOL
upstream opendoge {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 100M;

    location / {
        proxy_pass http://opendoge;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Enable site
ln -sf /etc/nginx/sites-available/opendoge /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Start application with Docker Compose
echo "Starting application..."
cd $APP_DIR
docker-compose -f docker-compose.prod.yml up -d

# Set up automatic updates for SSL certificate
echo "Setting up automatic SSL renewal..."
echo "0 0 * * * root certbot renew --quiet" > /etc/cron.d/certbot-renew

# Final steps
echo "
Setup completed successfully!

Your OpenDOGE instance is now running at https://$DOMAIN

Important information:
- Application directory: $APP_DIR
- Environment file: $APP_DIR/.env
- Logs: docker-compose -f docker-compose.prod.yml logs
- SSL certificates will auto-renew

To monitor the application:
- View logs: docker-compose -f docker-compose.prod.yml logs -f
- Check status: docker-compose -f docker-compose.prod.yml ps
- Restart: docker-compose -f docker-compose.prod.yml restart

Remember to:
1. Update the email in the script for SSL notifications
2. Secure your database password in .env
3. Set up any additional environment variables needed
4. Configure backups
" 