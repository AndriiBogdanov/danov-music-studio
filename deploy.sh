#!/bin/bash
# Deployment script for Danov Music Studio on VPS

echo "🚀 Starting deployment of Danov Music Studio..."

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@danovstudio.com', 'admin123')
    print("Superuser created: admin/admin123")
else:
    print("Superuser already exists")
EOF

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 manage.py
chmod -R 755 static/
chmod -R 755 staticfiles/

# Create logs directory
mkdir -p logs
chmod 755 logs

echo "✅ Deployment completed!"
echo "🌐 Server ready at: http://51.75.72.122:8000"
echo "👤 Admin panel: http://51.75.72.122:8000/admin/"
echo "📧 Admin login: admin / admin123"
