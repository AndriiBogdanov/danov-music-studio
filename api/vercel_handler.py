from http.server import BaseHTTPRequestHandler
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
from django.core.wsgi import get_wsgi_application

# Create WSGI application
application = get_wsgi_application()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Create a simple Django request
            factory = RequestFactory()
            
            # Create Django request
            django_request = factory.request(
                REQUEST_METHOD='GET',
                PATH_INFO=self.path,
                HTTP_HOST=self.headers.get('Host', 'localhost'),
            )
            
            # Process through Django
            response = application(django_request)
            
            # Send response
            self.send_response(response.status_code)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(error_msg.encode('utf-8')) 