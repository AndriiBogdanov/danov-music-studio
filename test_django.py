#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'danovmusic_studio.settings')

# Setup Django
django.setup()

# Test imports
try:
    from booking.views import portfolio, artists, contact, booking_view
    print("✅ All view functions imported successfully")
    
    from booking.urls import urlpatterns
    print("✅ URL patterns loaded successfully")
    
    print("✅ Django setup completed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

