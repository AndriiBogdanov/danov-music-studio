#!/bin/bash

# Deploy Danov Music Studio to VPS
# This script uploads and deploys the project to your VPS server

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration - EDIT THESE VALUES
SERVER_IP="51.75.72.122"                # Your VPS server IP
SERVER_USER="nikit"                     # SSH user
SSH_PASS="Qaz444666!"                   # SSH password
DOMAIN="www.danovmusic.com"             # Domain name
CUSTOM_PORT="2222"                      # SSH port
PROJECT_DIR="/home/nikit/danov-studio"

print_status "🚀 Starting deployment to VPS..."

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    print_warning "Installing sshpass for password authentication..."
    
    # Check OS and install sshpass
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install hudochenkov/sshpass/sshpass
        else
            print_error "Please install Homebrew or sshpass manually"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update && sudo apt-get install -y sshpass
    else
        print_error "Unsupported OS. Please install sshpass manually"
        exit 1
    fi
fi

# Create deployment package
print_status "Creating deployment package..."
tar -czf danov-studio-deploy.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='db.sqlite3' \
    --exclude='logs/*.log' \
    --exclude='staticfiles' \
    --exclude='.vercel' \
    --exclude='node_modules' \
    --exclude='danov-studio-deploy.tar.gz' \
    .

print_success "Package created: danov-studio-deploy.tar.gz"

# Upload package to server
print_status "Uploading package to server..."
sshpass -p "$SSH_PASS" scp -P $CUSTOM_PORT -o StrictHostKeyChecking=no danov-studio-deploy.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

print_success "Package uploaded to server"

# Connect to server and deploy
print_status "Connecting to server and deploying..."
sshpass -p "$SSH_PASS" ssh -p $CUSTOM_PORT -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
set -e

echo "🔧 Setting up environment on server..."

# Create sudo function
export SUDO_PASS="$SSH_PASS"
sudo_cmd() {
    echo "\$SUDO_PASS" | sudo -S "\$@"
}

# Update system
sudo_cmd apt update && sudo_cmd apt upgrade -y

# Install required packages
sudo_cmd apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git supervisor certbot python3-certbot-nginx ufw

# Create project directory
sudo_cmd mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Extract project
tar -xzf /tmp/danov-studio-deploy.tar.gz
rm /tmp/danov-studio-deploy.tar.gz

# Make scripts executable
chmod +x deploy_quick.sh deploy_vps.sh

# Set ownership
sudo_cmd chown -R www-data:www-data $PROJECT_DIR

# Run quick deployment
echo "🚀 Running quick deployment..."
sudo -u www-data bash << 'INNER_EOF'
cd $PROJECT_DIR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements_vps.txt

# Create .env file
if [ ! -f ".env" ]; then
    cp env_production_example.txt .env
    
    # Generate secret key
    SECRET_KEY=\$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/your-very-long-secret-key-here-generate-new-one/\$SECRET_KEY/" .env
    sed -i "s/yourdomain.com/$DOMAIN/" .env
    sed -i "s/your-server-ip/$SERVER_IP/" .env
fi

# Create directories
mkdir -p logs media staticfiles

# Set Django settings
export DJANGO_SETTINGS_MODULE=danovmusic_studio.settings_vps

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (using SQLite for now)
python manage.py migrate

echo "✅ Application setup completed"
INNER_EOF

# Setup PostgreSQL database
echo "🗄️ Setting up PostgreSQL..."
sudo -u postgres createuser --createdb danovmusic_user || true
sudo -u postgres createdb danovmusic_db -O danovmusic_user || true
sudo -u postgres psql -c "ALTER USER danovmusic_user PASSWORD 'danov_db_2024!';" || true

# Setup Gunicorn with Supervisor
echo "⚙️ Setting up Gunicorn service..."
sudo bash -c "cat > /etc/supervisor/conf.d/danov-studio.conf << 'SUPERVISOR_EOF'
[program:danov-studio]
command=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind unix:$PROJECT_DIR/danov-studio.sock danovmusic_studio.wsgi:application
directory=$PROJECT_DIR
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/danov-studio.log
environment=DJANGO_SETTINGS_MODULE="danovmusic_studio.settings_vps"
SUPERVISOR_EOF"

# Setup Nginx
echo "🌐 Setting up Nginx..."
sudo cp nginx_danov_studio.conf /etc/nginx/sites-available/danov-studio

# Update domain and port in nginx config
sudo sed -i "s/217.154.120.187/$DOMAIN/g" /etc/nginx/sites-available/danov-studio
sudo sed -i "s/8847/$CUSTOM_PORT/g" /etc/nginx/sites-available/danov-studio
sudo sed -i "s|/var/www/danov-studio|$PROJECT_DIR|g" /etc/nginx/sites-available/danov-studio

# Enable site
sudo ln -sf /etc/nginx/sites-available/danov-studio /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx config
sudo nginx -t

# Start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start danov-studio
sudo systemctl restart nginx
sudo systemctl enable nginx supervisor

# Setup SSL Certificate
echo "🔒 Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@danovmusic.com

# Setup firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
echo "y" | sudo ufw enable

echo "🎉 Deployment completed!"
echo "🌐 Your site should be available at: https://$DOMAIN"
echo "🔒 SSL certificate installed"

EOF

# Clean up local package
rm danov-studio-deploy.tar.gz

print_success "🎉 Deployment completed successfully!"
print_status "🌐 Your site should be available at: http://$DOMAIN:$CUSTOM_PORT"
print_warning "📝 Next steps:"
print_warning "1. Test the site at: http://$SERVER_IP:$CUSTOM_PORT"
print_warning "2. Edit .env file on server with your actual email settings"
print_warning "3. Test the booking form and email notifications"
print_warning "4. Custom port $CUSTOM_PORT used for security"

print_status "🔧 Useful commands for server management:"
echo "ssh root@$SERVER_IP"
echo "sudo supervisorctl status danov-studio"
echo "sudo supervisorctl restart danov-studio"
echo "sudo tail -f /var/log/danov-studio.log"
