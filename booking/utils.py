import secrets
import hashlib
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from datetime import datetime, timedelta


def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def generate_booking_tokens(booking):
    """Generate confirmation and rejection tokens for a booking"""
    booking.confirmation_token = generate_token()
    booking.rejection_token = generate_token()
    booking.save()
    return booking.confirmation_token, booking.rejection_token


def send_booking_notification_email(booking, request):
    """Send notification email to studio about new booking request"""
    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
    
    subject = f'New Studio Booking Request from {booking.name}'
    
    # Generate confirmation and rejection URLs
    confirm_url = f"{base_url}/booking/confirm/{booking.id}/"
    reject_url = f"{base_url}/booking/reject/{booking.id}/"
    email_client_url = f"mailto:{booking.email}?subject=Re: Booking Request #{booking.id}"
    
    # Generate HTML content using template
    html_content = render_to_string('booking/email/booking_notification.html', {
        'booking': booking,
        'base_url': base_url,
        'confirm_url': confirm_url,
        'reject_url': reject_url,
        'email_client_url': email_client_url
    })
    
    # Plain text fallback
    text_content = f"""
=======================================
     NEW BOOKING REQUEST - DANOV MUSIC STUDIO
=======================================

A new booking request has been submitted and requires your review.

BOOKING DETAILS:
--------------------
Name: {booking.name}
Email: {booking.email}
Phone: {booking.phone}
Date: {booking.date.strftime('%B %d, %Y')}
Time: {booking.time.strftime('%H:%M')}
Duration: {booking.get_duration_display()}
Service: {booking.get_service_display() or 'Not specified'}

CLIENT MESSAGE:
------------------
{booking.message or 'No additional message provided'}

BOOKING ID: #{booking.id}

=======================================
Please visit our website and make a decision through the admin panel:
{base_url}/admin/booking/booking/{booking.id}/

Best regards,
Danov Music Studio Website System
    """
    
    try:
        # Send email to studio with HTML content
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.BOOKING_NOTIFICATION_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Use SSL context for Mac compatibility
        if hasattr(settings, 'EMAIL_SSL_CONTEXT'):
            email.connection = email.get_connection()
            email.connection.ssl_context = settings.EMAIL_SSL_CONTEXT
        
        email.send()
        
        # Mark email as sent
        booking.email_sent = True
        booking.email_sent_at = timezone.now()
        booking.save()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_booking_pending_email(booking, request):
    """Send notification to client that booking is under review"""
    base_url = request.build_absolute_uri('/')[:-1]
    
    subject = f'Booking Request Received - Danov Music Studio'
    
    # Generate HTML content using template
    html_content = render_to_string('booking/email/booking_pending.html', {
        'booking': booking,
        'base_url': base_url
    })
    
    # Plain text fallback
    text_content = f"""
=======================================
     BOOKING REQUEST RECEIVED - DANOV MUSIC STUDIO
=======================================

Dear {booking.name},

Thank you for your booking request! We have received your application and it is currently under review.

BOOKING DETAILS:
--------------------
Service: {booking.get_service_display() or 'Not specified'}
Date: {booking.date.strftime('%B %d, %Y')}
Time: {booking.time.strftime('%H:%M')}
Duration: {booking.get_duration_display()}

BOOKING ID: #{booking.id}

=======================================
We will review your request and contact you soon with our decision.

If you have any questions, please contact us:
Phone: +49 175 413 75 18
Email: danovmusic@gmail.com

Best regards,
Danov Music Studio Team
    """
    
    try:
        # Send HTML email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Use SSL context for Mac compatibility
        if hasattr(settings, 'EMAIL_SSL_CONTEXT'):
            email.connection = email.get_connection()
            email.connection.ssl_context = settings.EMAIL_SSL_CONTEXT
        
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send pending email: {e}")
        return False


def send_booking_confirmation_email(booking, request):
    """Send confirmation email to client"""
    base_url = request.build_absolute_uri('/')[:-1]
    
    subject = f'Booking Confirmed - Danov Music Studio'
    
    # Generate HTML content using template
    html_content = render_to_string('booking/email/booking_confirmed.html', {
        'booking': booking,
        'base_url': base_url
    })
    
    # Plain text fallback
    text_content = f"""
=======================================
     BOOKING CONFIRMED - DANOV MUSIC STUDIO
=======================================

Dear {booking.name},

Great news! Your booking has been confirmed!

BOOKING DETAILS:
--------------------
Service: {booking.get_service_display() or 'Not specified'}
Date: {booking.date.strftime('%B %d, %Y')}
Time: {booking.time.strftime('%H:%M')}
Duration: {booking.get_duration_display()}

STUDIO LOCATION:
--------------------
Danov Music Studio
Bonifaziusstraße 16-18
13509 Berlin, Germany

CONTACT INFORMATION:
-----------------------
Phone: +49 175 413 75 18
Email: danovmusic@gmail.com

IMPORTANT REMINDERS:
------------------------
• Please arrive 10 minutes before your scheduled time
• Bring any necessary equipment or files
• Contact us if you need to reschedule

Thank you for choosing Danov Music Studio!

Best regards,
Danov Music Studio Team
    """
    
    try:
        # Send email with HTML content
        from django.core.mail import EmailMultiAlternatives
        
        print(f"Attempting to send confirmation email to {booking.email}")
        print(f"From: {settings.DEFAULT_FROM_EMAIL}")
        print(f"Subject: {subject}")
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Use SSL context for Mac compatibility
        if hasattr(settings, 'EMAIL_SSL_CONTEXT'):
            email.connection = email.get_connection()
            email.connection.ssl_context = settings.EMAIL_SSL_CONTEXT
        
        email.send()
        print(f"Confirmation email sent successfully to {booking.email}")
        return True
    except Exception as e:
        print(f"Failed to send confirmation email to {booking.email}: {e}")
        return False


def send_booking_rejection_email(booking, request):
    """Send rejection email to client"""
    base_url = request.build_absolute_uri('/')[:-1]
    
    subject = f'Booking Cancelled - Danov Music Studio'
    
    # Generate HTML content using template
    html_content = render_to_string('booking/email/booking_rejected.html', {
        'booking': booking,
        'base_url': base_url
    })
    
    # Plain text fallback
    text_content = f"""
=======================================
     BOOKING CANCELLED - DANOV MUSIC STUDIO
=======================================

Dear {booking.name},

Unfortunately, we cannot accommodate your booking request for the requested date and time. This could be due to unforeseen schedule changes, personal commitments, or previous bookings that we may have overlooked.

We apologize for any inconvenience this may cause.

BOOKING DETAILS:
--------------------
Service: {booking.get_service_display() or 'Not specified'}
Date: {booking.date.strftime('%B %d, %Y')}
Time: {booking.time.strftime('%H:%M')}
Duration: {booking.get_duration_display()}

=======================================
Please try selecting different dates and times on our website:
{base_url}/booking/

Or call us at +49 175 413 75 18 to discuss alternative options and book a new appointment.

We are ready to work with you, just this specific time is not available.

Best regards,
Danov Music Studio Team
    """
    
    try:
        # Send email with HTML content
        from django.core.mail import EmailMultiAlternatives
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Use SSL context for Mac compatibility
        if hasattr(settings, 'EMAIL_SSL_CONTEXT'):
            email.connection = email.get_connection()
            email.connection.ssl_context = settings.EMAIL_SSL_CONTEXT
        
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send rejection email: {e}")
        return False
