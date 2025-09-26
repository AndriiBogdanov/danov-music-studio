#!/bin/bash

# Quick VPS Deployment Script for Danov Music Studio
# Run this on your VPS server after uploading the files

set -e

echo "🚀 Quick deployment for Danov Music Studio..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Update packages
print_status "Installing basic requirements..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx git

# Create virtual environment
print_status "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
print_status "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements_vps.txt

# Set up environment variables
if [ ! -f ".env" ]; then
    print_warning "Creating .env file from template..."
    cp env_production_example.txt .env
    print_warning "❗ Please edit .env file with your actual values!"
    print_warning "❗ Don't forget to set your domain in ALLOWED_HOSTS!"
fi

# Generate secret key
print_status "Generating Django secret key..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "Generated SECRET_KEY: $SECRET_KEY"
print_warning "Add this to your .env file: SECRET_KEY=$SECRET_KEY"

# Create directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Set Django settings
export DJANGO_SETTINGS_MODULE=danovmusic_studio.settings_vps

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
print_status "Running database migrations..."
python manage.py migrate

print_success "🎉 Quick setup completed!"
print_warning "Next steps:"
print_warning "1. Edit .env file with your actual values"
print_warning "2. Set up Nginx configuration"
print_warning "3. Set up SSL certificate"
print_warning "4. Configure your domain DNS"

print_status "To test the application, run:"
print_status "source venv/bin/activate"
print_status "export DJANGO_SETTINGS_MODULE=danovmusic_studio.settings_vps"
print_status "python manage.py runserver 0.0.0.0:8000"



