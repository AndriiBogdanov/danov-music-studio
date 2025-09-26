#!/bin/bash

# Simple VPS Deployment for Danov Music Studio
# Uses manual approach to avoid sudo password issues

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

# Configuration
SERVER_IP="217.154.120.187"
SERVER_USER="adminuser"
SSH_PASS="8mAsOR27"
CUSTOM_PORT="8847"
PROJECT_DIR="/var/www/danov-studio"

print_status "🚀 Starting simple deployment to VPS..."

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
    --exclude='*.tar.gz' \
    .

print_success "Package created: danov-studio-deploy.tar.gz"

# Upload package to server
print_status "Uploading package to server..."
sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=no danov-studio-deploy.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

print_success "Package uploaded to server"

# Create setup script for server
print_status "Creating server setup script..."
cat > server_setup.sh << 'SETUP_EOF'
#!/bin/bash
set -e

echo "🔧 Setting up Danov Music Studio on server..."

# Update system (will ask for password)
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx git

# Create project directory
sudo mkdir -p /var/www/danov-studio
cd /var/www/danov-studio

# Extract project
sudo tar -xzf /tmp/danov-studio-deploy.tar.gz
sudo rm /tmp/danov-studio-deploy.tar.gz

# Set ownership to current user for now
sudo chown -R $USER:$USER /var/www/danov-studio

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
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/your-very-long-secret-key-here-generate-new-one/$SECRET_KEY/" .env
    echo "✅ .env file created with generated secret key"
fi

# Create directories
mkdir -p logs media staticfiles

# Set Django settings
export DJANGO_SETTINGS_MODULE=danovmusic_studio.settings_vps

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

echo "✅ Basic setup completed!"
echo "📝 Next steps:"
echo "1. Configure Nginx: sudo cp nginx_danov_studio.conf /etc/nginx/sites-available/danov-studio"
echo "2. Edit Nginx config and enable site"
echo "3. Install supervisor and configure Gunicorn"
echo "4. Test the application"

SETUP_EOF

# Upload setup script
print_status "Uploading setup script to server..."
sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=no server_setup.sh $SERVER_USER@$SERVER_IP:/tmp/

# Run setup script on server
print_status "Running setup script on server..."
sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "chmod +x /tmp/server_setup.sh && /tmp/server_setup.sh"

# Clean up local files
rm danov-studio-deploy.tar.gz server_setup.sh

print_success "🎉 Basic deployment completed!"
print_warning "🔧 Manual steps remaining:"
print_warning "1. SSH to server: ssh $SERVER_USER@$SERVER_IP"
print_warning "2. Configure Nginx on port $CUSTOM_PORT"
print_warning "3. Setup Supervisor for Gunicorn"
print_warning "4. Configure firewall"
print_warning "5. Test at http://$SERVER_IP:$CUSTOM_PORT"

print_status "To complete setup, run these commands on server:"
echo "sudo cp /var/www/danov-studio/nginx_danov_studio.conf /etc/nginx/sites-available/danov-studio"
echo "sudo ln -s /etc/nginx/sites-available/danov-studio /etc/nginx/sites-enabled/"
echo "sudo rm /etc/nginx/sites-enabled/default"
echo "sudo systemctl restart nginx"




