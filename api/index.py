import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'danovmusic_studio.settings_prod')

# Import Django
import django
django.setup()

from django.http import HttpResponse
from django.urls import resolve
from django.test import RequestFactory
from django.core.handlers.wsgi import WSGIRequest
from django.core.wsgi import get_wsgi_application

# Create WSGI application
application = get_wsgi_application()

# Vercel handler
def handler(request, context):
    try:
        # Create a simple Django request
        factory = RequestFactory()
        path = request.get('path', '/')
        method = request.get('method', 'GET')
        
        # Create Django request
        django_request = factory.request(
            REQUEST_METHOD=method,
            PATH_INFO=path,
            HTTP_HOST=request.get('headers', {}).get('host', 'localhost'),
        )
        
        # Process through Django
        response = application(django_request)
        
        # Convert response
        return {
            'statusCode': response.status_code,
            'headers': {'Content-Type': 'text/html; charset=utf-8'},
            'body': response.content.decode('utf-8')
        }
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain; charset=utf-8'},
            'body': error_msg
        } 