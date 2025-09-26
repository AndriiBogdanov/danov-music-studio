#!/bin/bash

# VPS Deployment Script for Danov Music Studio
# This script deploys the Django application to a VPS server

set -e  # Exit on any error

echo "🚀 Starting VPS deployment for Danov Music Studio..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (edit these values)
PROJECT_NAME="danov-studio"
PROJECT_DIR="/var/www/$PROJECT_NAME"
REPO_URL="your-git-repo-url"  # Replace with your git repository URL
DOMAIN="yourdomain.com"       # Replace with your domain
EMAIL="danovmusic@gmail.com"  # Replace with your email for SSL

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (use sudo)"
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git certbot python3-certbot-nginx supervisor

# Create project user
print_status "Creating project user..."
if ! id "$PROJECT_NAME" &>/dev/null; then
    useradd -m -s /bin/bash $PROJECT_NAME
    print_success "User $PROJECT_NAME created"
else
    print_warning "User $PROJECT_NAME already exists"
fi

# Create project directory
print_status "Setting up project directory..."
mkdir -p $PROJECT_DIR
chown $PROJECT_NAME:$PROJECT_NAME $PROJECT_DIR

# Switch to project user for the rest of the setup
print_status "Switching to project user..."
sudo -u $PROJECT_NAME bash << EOF
cd $PROJECT_DIR

# Clone or update repository
if [ -d ".git" ]; then
    print_status "Updating existing repository..."
    git pull origin main
else
    print_status "Cloning repository..."
    git clone $REPO_URL .
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cp environment_variables.example .env
    print_warning "Please edit .env file with your actual values!"
fi

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
print_status "Running database migrations..."
python manage.py migrate

# Create superuser if needed
print_status "Creating superuser (if needed)..."
python manage.py createsuperuser --noinput --username admin --email $EMAIL || true

EOF

# Create Gunicorn configuration
print_status "Creating Gunicorn configuration..."
cat > /etc/supervisor/conf.d/$PROJECT_NAME.conf << EOF
[program:$PROJECT_NAME]
command=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/$PROJECT_NAME.sock danovmusic_studio.wsgi:application
directory=$PROJECT_DIR
user=$PROJECT_NAME
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/$PROJECT_NAME.log
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/$PROJECT_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root $PROJECT_DIR;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        root $PROJECT_DIR;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/$PROJECT_NAME.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    client_max_body_size 100M;
}
EOF

# Enable Nginx site
print_status "Enabling Nginx site..."
ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_status "Testing Nginx configuration..."
nginx -t

# Start services
print_status "Starting services..."
supervisorctl reread
supervisorctl update
supervisorctl start $PROJECT_NAME
systemctl restart nginx
systemctl enable nginx
systemctl enable supervisor

# Setup SSL with Let's Encrypt
print_status "Setting up SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL

print_success "🎉 Deployment completed successfully!"
print_status "Your site should now be available at: https://$DOMAIN"
print_warning "Don't forget to:"
print_warning "1. Edit $PROJECT_DIR/.env with your actual values"
print_warning "2. Update ALLOWED_HOSTS in Django settings"
print_warning "3. Configure your DNS to point to this server"
print_warning "4. Set up email settings for notifications"



