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

