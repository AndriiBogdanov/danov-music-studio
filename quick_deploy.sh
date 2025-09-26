#!/bin/bash
# Quick deploy script for after BIOS setup

echo "🚀 Danov Music Studio - VPS Deploy"
echo "=================================="

VPS_HOST="217.154.120.187"
VPS_USER="adminuser"
VPS_PASSWORD="8mAsOR27"
SUDO_PASSWORD="Qaz444666!"

echo "📡 Connecting to $VPS_USER@$VPS_HOST"

# Try to deploy automatically
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" << 'EOF'
echo "🔍 Finding project directory..."
if [ -d "/var/www/danov-studio" ]; then
    PROJECT_DIR="/var/www/danov-studio"
elif [ -d "/var/www/danov-music-studio" ]; then
    PROJECT_DIR="/var/www/danov-music-studio"
elif [ -d "/home/adminuser/danov-studio" ]; then
    PROJECT_DIR="/home/adminuser/danov-studio"
else
    echo "❌ Project directory not found!"
    exit 1
fi

echo "📂 Found project at: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "📥 Pulling latest changes..."
git pull origin master

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Restarting service..."
echo "Qaz444666!" | sudo -S systemctl restart danov-studio

echo "✅ Deployment completed!"
echo "🌐 Site available at: http://217.154.120.187:8847"

echo "📊 Service status:"
sudo systemctl status danov-studio --no-pager
EOF

echo "🎉 Deploy script completed!"

