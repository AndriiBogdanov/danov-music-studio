#!/bin/bash

# Danov Music Studio - SSL Setup and Deployment Script
# This script sets up SSL certificate and deploys the Django application

set -e

echo "🎵 Danov Music Studio - SSL Setup & Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as regular user."
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y nginx certbot python3-certbot-nginx ufw

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Stop any running Django processes
print_status "Stopping existing Django processes..."
pkill -f "python.*manage.py" || true
pkill -f gunicorn || true

# Navigate to project directory
cd /home/nikit/danov-studio

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Copy production environment file
print_status "Setting up environment variables..."
cp production.env .env

# Run Django management commands
print_status "Running Django migrations..."
python manage.py migrate

print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Set proper permissions
print_status "Setting file permissions..."
chmod -R 755 /home/nikit/danov-studio
chmod -R 644 /home/nikit/danov-studio/staticfiles/*

# Configure Nginx
print_status "Configuring Nginx..."
sudo cp nginx_danovmusic.conf /etc/nginx/sites-available/danovmusic.com
sudo ln -sf /etc/nginx/sites-available/danovmusic.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Start Nginx
print_status "Starting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# Obtain SSL certificate
print_status "Obtaining SSL certificate from Let's Encrypt..."
sudo certbot --nginx -d www.danovmusic.com --non-interactive --agree-tos --email admin@danovmusic.com

# Start Django with Gunicorn
print_status "Starting Django application with Gunicorn..."
nohup gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 120 danovmusic_studio.wsgi:application > gunicorn.log 2>&1 &

# Wait a moment for the application to start
sleep 5

# Test the application
print_status "Testing application..."
if curl -s -o /dev/null -w "%{http_code}" https://www.danovmusic.com | grep -q "200"; then
    print_status "✅ Application is running successfully!"
    print_status "🌐 Website: https://www.danovmusic.com"
    print_status "🔒 SSL Certificate: Active"
else
    print_warning "Application might not be fully ready yet. Please check manually."
fi

# Show status
print_status "Deployment completed!"
echo ""
echo "📋 Summary:"
echo "  - Domain: www.danovmusic.com"
echo "  - SSL: Enabled (Let's Encrypt)"
echo "  - Nginx: Running"
echo "  - Django: Running on Gunicorn"
echo "  - Static files: Collected"
echo ""
echo "🔧 Useful commands:"
echo "  - Check Django logs: tail -f /home/nikit/danov-studio/gunicorn.log"
echo "  - Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "  - Restart Django: pkill -f gunicorn && cd /home/nikit/danov-studio && source venv/bin/activate && nohup gunicorn --bind 127.0.0.1:8000 --workers 3 danovmusic_studio.wsgi:application > gunicorn.log 2>&1 &"
echo "  - Renew SSL: sudo certbot renew"
echo ""
print_status "🎉 Danov Music Studio is now live at https://www.danovmusic.com!"
