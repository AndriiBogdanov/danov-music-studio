from django.http import HttpResponseForbidden
from django.utils import timezone
from django.shortcuts import render
from datetime import timedelta
from .models import IPTracker, SpamLog, Booking
import logging

logger = logging.getLogger(__name__)


class AntiSpamMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip anti-spam for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)
        
        client_ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check if IP is blocked
        try:
            ip_tracker, created = IPTracker.objects.get_or_create(
                ip_address=client_ip,
                defaults={
                    'booking_count': 0,
                    'is_blocked': False
                }
            )
            
            if ip_tracker.is_blocked:
                # Log blocked attempt
                SpamLog.objects.create(
                    ip_address=client_ip,
                    user_agent=user_agent,
                    attempt_type='suspicious',
                    details=f'Blocked IP attempted access: {request.path}'
                )
                
                return HttpResponseForbidden(
                    self.render_blocked_page(request, ip_tracker.block_reason)
                )
            
            # Check rate limiting for booking submissions
            if request.method == 'POST' and 'booking' in request.path:
                if ip_tracker.is_rate_limited():
                    # Log rate limit attempt
                    SpamLog.objects.create(
                        ip_address=client_ip,
                        user_agent=user_agent,
                        attempt_type='rate_limit',
                        details=f'Rate limited: {request.path}'
                    )
                    
                    return HttpResponseForbidden(
                        self.render_rate_limit_page(request)
                    )
            
            # Update IP tracker only if needed
            # Don't save on every request to avoid database spam
            
        except Exception as e:
            logger.error(f"Anti-spam middleware error: {e}")
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get the real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def render_blocked_page(self, request, reason):
        """Render blocked page"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Access Blocked - Danov Music Studio</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    background: #000; 
                    color: #fff; 
                    text-align: center; 
                    padding: 50px; 
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: #1a1a1a; 
                    padding: 30px; 
                    border-radius: 10px; 
                }}
                h1 {{ color: #dc3545; }}
                .reason {{ 
                    background: #2a2a2a; 
                    padding: 20px; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚫 Access Blocked</h1>
                <div class="reason">
                    <p><strong>Reason:</strong> {reason}</p>
                </div>
                <p>If you believe this is an error, please contact us:</p>
                <p>📧 danovmusic@gmail.com<br>📞 +49 175 413 75 18</p>
            </div>
        </body>
        </html>
        """

    def render_rate_limit_page(self, request):
        """Render rate limit page"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rate Limited - Danov Music Studio</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    background: #000; 
                    color: #fff; 
                    text-align: center; 
                    padding: 50px; 
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: #1a1a1a; 
                    padding: 30px; 
                    border-radius: 10px; 
                }}
                h1 {{ color: #ffc107; }}
                .info {{ 
                    background: #2a2a2a; 
                    padding: 20px; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⏰ Rate Limited</h1>
                <div class="info">
                    <p>You have made too many booking requests in a short time.</p>
                    <p><strong>Limit:</strong> 3 bookings per hour</p>
                    <p><strong>Please wait:</strong> 1 hour before making another request</p>
                </div>
                <p>If you need urgent assistance, please contact us:</p>
                <p>📧 danovmusic@gmail.com<br>📞 +49 175 413 75 18</p>
            </div>
        </body>
        </html>
        """ 