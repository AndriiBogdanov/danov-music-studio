from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from django.conf import settings
from .models import SiteSEOSettings, PageSEO
from datetime import datetime, timedelta
from .forms import BookingForm
from .models import Booking, IPTracker, SpamLog, StudioSchedule, TimeSlot
from .utils import send_booking_notification_email, send_booking_pending_email, send_booking_confirmation_email, send_booking_rejection_email
import uuid
import logging

# Security logger
security_logger = logging.getLogger('django.security')

def home(request):
    """Главная страница сайта с языковыми шаблонами"""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/home_en.html',
        'ru': 'booking/home_ru.html',
        'uk': 'booking/home_uk.html',
        'de': 'booking/home_de.html',
    }
    template_name = template_map.get(lang, 'booking/home_en.html')
    # PageSEO override
    path = request.path
    lang = lang
    page_seo = PageSEO.objects.filter(path__in=[path, path.rstrip('/') + '/'], language=lang).first()
    default_seo = SiteSEOSettings.objects.first()
    seo = {
        'description': _('Recording studio in Berlin: recording, mixing, mastering, production. Ukrainian studio in Berlin.'),
        'keywords': 'recording studio berlin, mixing berlin, mastering berlin, ukrainian recording studio berlin',
        'og_title': 'Danov Music Studio – Recording Studio in Berlin',
        'og_description': _('Professional recording, mixing, mastering and production in Berlin.'),
    }
    if default_seo:
        seo.setdefault('description', default_seo.default_description or seo['description'])
        seo.setdefault('keywords', default_seo.default_keywords or seo['keywords'])
        if default_seo.gtag_enabled and default_seo.ga4_measurement_id:
            seo['ga4'] = {'id': default_seo.ga4_measurement_id}
    if page_seo:
        if page_seo.title:
            # title передаётся в блок title через шаблон, мета остаются тут
            pass
        if page_seo.description:
            seo['description'] = page_seo.description
        if page_seo.keywords:
            seo['keywords'] = page_seo.keywords
        if page_seo.og_title:
            seo['og_title'] = page_seo.og_title
        if page_seo.og_description:
            seo['og_description'] = page_seo.og_description
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/')},
    ]
    return render(request, template_name, {'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/')})

def about(request):
    """Страница о студии с языковыми шаблонами"""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/about_en.html',
        'ru': 'booking/about_ru.html',
        'uk': 'booking/about_uk.html',
        'de': 'booking/about_de.html',
    }
    template_name = template_map.get(lang, 'booking/about_en.html')
    seo = {
        'description': _('About Danov Music Studio in Berlin: first Ukrainian-led recording studio. Equipment, experience, values.'),
        'keywords': 'about recording studio berlin, ukrainian studio berlin',
        'og_title': 'About – Danov Music Studio Berlin',
        'og_description': _('Learn about our team, equipment and mission.'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/about/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/about/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/about/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/about/')},
    ]
    return render(request, template_name, {'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/about/')})

def services(request):
    """Страница услуг с языковыми шаблонами"""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/services_en.html',
        'ru': 'booking/services_ru.html',
        'uk': 'booking/services_uk.html',
        'de': 'booking/services_de.html',
    }
    template_name = template_map.get(lang, 'booking/services_en.html')
    seo = {
        'description': _('Services: Recording, Mixing, Mastering, Production in Berlin. Transparent pricing.'),
        'keywords': 'recording berlin, mixing berlin, mastering berlin, music production berlin',
        'og_title': 'Services – Danov Music Studio Berlin',
        'og_description': _('Professional audio services in Berlin.'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/services/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/services/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/services/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/services/')},
    ]
    return render(request, template_name, {'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/services/')})

def equipment(request):
    """Страница оборудования с языковыми шаблонами"""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/equipment_en.html',
        'ru': 'booking/equipment_ru.html',
        'uk': 'booking/equipment_uk.html',
        'de': 'booking/equipment_de.html',
    }
    template_name = template_map.get(lang, 'booking/equipment_en.html')
    seo = {
        'description': _('Studio equipment: Neumann, Genelec, Yamaha, high-end gear in Berlin.'),
        'keywords': 'recording equipment berlin, genelec berlin, neumann berlin',
        'og_title': 'Equipment – Danov Music Studio Berlin',
        'og_description': _('High-end equipment for professional sound.'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/equipment/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/equipment/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/equipment/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/equipment/')},
    ]
    return render(request, template_name, {'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/equipment/')})

def gallery(request):
    """Страница галереи"""
    return render(request, 'booking/gallery.html')

def portfolio(request):
    """Страница портфолио с языковыми шаблонами"""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/portfolio_en.html',
        'ru': 'booking/portfolio_ru.html',
        'uk': 'booking/portfolio_uk.html',
        'de': 'booking/portfolio_de.html',
    }
    template_name = template_map.get(lang, 'booking/portfolio_en.html')
    seo = {
        'description': _('Portfolio: artists and projects recorded, mixed, mastered in Berlin.'),
        'keywords': 'portfolio recording berlin, artists berlin studio',
        'og_title': 'Portfolio – Danov Music Studio Berlin',
        'og_description': _('Selected works and artists we worked with.'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/portfolio/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/portfolio/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/portfolio/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/portfolio/')},
    ]
    return render(request, template_name, {'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/portfolio/')})

def contact(request):
    """Страница контактов с языковыми шаблонами"""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/contact_en.html',
        'ru': 'booking/contact_ru.html',
        'uk': 'booking/contact_uk.html',
        'de': 'booking/contact_de.html',
    }
    template_name = template_map.get(lang, 'booking/contact_en.html')
    seo = {
        'description': _('Contact Danov Music Studio in Berlin: phone, email, address, working hours.'),
        'keywords': 'contact recording studio berlin',
        'og_title': 'Contact – Danov Music Studio Berlin',
        'og_description': _('Get in touch for booking and questions.'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/contact/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/contact/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/contact/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/contact/')},
    ]
    return render(request, template_name, {'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/contact/')})

def artists(request):
    """Страница артистов с языковыми шаблонами"""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/artists_en.html',
        'ru': 'booking/artists_ru.html',
        'uk': 'booking/artists_uk.html',
        'de': 'booking/artists_de.html',
    }
    template_name = template_map.get(lang, 'booking/artists_en.html')
    seo = {
        'description': _('Artists who worked with Danov Music Studio in Berlin.'),
        'keywords': 'artists berlin studio, clients berlin recording',
        'og_title': 'Artists – Danov Music Studio Berlin',
        'og_description': _('Artists and collaborators'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/artists/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/artists/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/artists/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/artists/')},
    ]
    return render(request, template_name, {'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/artists/')})

def faq(request):
    """Общая FAQ страница с языковыми шаблонами"""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/faq_en.html',
        'ru': 'booking/faq_ru.html',
        'uk': 'booking/faq_uk.html',
        'de': 'booking/faq_de.html',
    }
    template_name = template_map.get(lang, 'booking/faq_en.html')
    seo = {
        'description': _('Frequently Asked Questions about booking, services, payments and cancellations.'),
        'keywords': 'faq recording studio berlin, booking faq, services faq',
        'og_title': 'FAQ – Danov Music Studio Berlin',
        'og_description': _('Answers about booking, services, payments and more.'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/faq/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/faq/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/faq/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/faq/')},
    ]
    return render(request, template_name, {'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/faq/')})

def get_available_times(date_str):
    """Get available time slots for a given date"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return []
    
    # Only show times for today and future dates
    if date < timezone.now().date():
        return []
    
    # Check if date is blocked in studio schedule
    if not StudioSchedule.is_date_available(date):
        return []
    
    # Studio hours: 9:00 AM - 9:30 PM (Mon-Fri)
    start_hour = 9
    end_hour = 21
    end_minute = 30
    
    # Generate all possible time slots
    available_times = []
    current_time = datetime.combine(date, datetime.min.time().replace(hour=start_hour))
    end_time = datetime.combine(date, datetime.min.time().replace(hour=end_hour, minute=end_minute))
    
    while current_time < end_time:
        time_str = current_time.strftime('%H:%M')
        # Check if this specific time slot is available
        if TimeSlot.is_time_available(date, time_str):
            available_times.append(time_str)
        current_time += timedelta(hours=1)
    
    return available_times


def get_all_times_with_status(date_str):
    """Get all time slots with availability status"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return []
    
    # Only show times for today and future dates
    if date < timezone.now().date():
        return []
    
    # Check if date is blocked in studio schedule
    date_blocked = not StudioSchedule.is_date_available(date)
    
    # Studio hours: 9:00 AM - 9:30 PM (Mon-Fri)
    start_hour = 9
    end_hour = 21
    end_minute = 30
    
    # Generate all possible time slots
    all_times = []
    current_time = datetime.combine(date, datetime.min.time().replace(hour=start_hour))
    end_time = datetime.combine(date, datetime.min.time().replace(hour=end_hour, minute=end_minute))
    
    while current_time < end_time:
        time_str = current_time.strftime('%H:%M')
        all_times.append(time_str)
        current_time += timedelta(hours=1)
    
    # Get all time slots for this date
    time_slots = TimeSlot.objects.filter(date=date)
    blocked_slots = {slot.time: slot for slot in time_slots if slot.is_blocked or slot.is_booked}
    
    # Get confirmed bookings for this date to block multiple hours
    confirmed_bookings = Booking.objects.filter(
        date=date,
        status='confirmed'
    ).values_list('time', 'duration')
    
    # Block all hours for each booking duration
    for start_time, duration in confirmed_bookings:
        start_hour = start_time.hour
        for hour in range(duration):
            blocked_time = f"{start_hour + hour:02d}:00"
            if blocked_time not in blocked_slots:
                blocked_slots[blocked_time] = None  # Mark as booked
    
    # Create time slots with status
    time_slots_with_status = []
    for time_str in all_times:
        if date_blocked:
            # If date is blocked, all slots are blocked
            status = 'blocked'
            reason = "Date blocked"
        else:
            slot = blocked_slots.get(time_str)
            if slot is None:
                # Check if this time is blocked by a booking duration
                if time_str in blocked_slots:
                    status = 'booked'
                    reason = "Booked"
                else:
                    status = 'available'
                    reason = ""
            elif slot.is_blocked:
                status = 'blocked'
                reason = slot.reason
            else:
                status = 'booked'
                reason = f"Booked by {slot.booking.name}" if slot.booking else "Booked"
        
        time_slots_with_status.append({
            'time': time_str,
            'status': status,
            'reason': reason,
            'available': status == 'available'
        })
    
    return time_slots_with_status

def get_client_ip(request):
    """Get the real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_duplicate_booking(ip_address, email, phone, date, time):
    """Check for duplicate bookings"""
    # Check for exact duplicate in last 10 minutes
    ten_minutes_ago = timezone.now() - timedelta(minutes=10)
    
    duplicate = Booking.objects.filter(
        ip_address=ip_address,
        email=email,
        phone=phone,
        date=date,
        time=time,
        created_at__gte=ten_minutes_ago
    ).first()
    
    return duplicate is not None


def booking_view(request):
    """Страница бронирования (логика + выбор языкового шаблона)"""
    selected_service = request.GET.get('service', '')
    
    # Save selected service to session if provided
    if selected_service:
        request.session['selected_service'] = selected_service
    
    # Get service from session if not in URL
    if not selected_service:
        selected_service = request.session.get('selected_service', '')
    
    # Cache available dates to avoid multiple database queries
    from django.core.cache import cache
    cache_key = 'available_dates'
    available_dates = cache.get(cache_key)
    
    if available_dates is None:
        # Generate available dates (next 7 days)
        available_dates = []
        for i in range(7):
            date = timezone.now().date() + timedelta(days=i)
            # Skip weekends
            if date.weekday() < 5:  # Monday = 0, Friday = 4
                times = get_all_times_with_status(date.strftime('%Y-%m-%d'))
                # Always add the date, even if all times are blocked
                available_dates.append({
                    'date': date,
                    'times': times
                })
        
        # Cache for 5 minutes
        cache.set(cache_key, available_dates, 300)
    
    if request.method == 'POST':
        print(f"POST request received: {request.POST}")  # Debug info
        form = BookingForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")  # Debug info
        if not form.is_valid():
            print(f"Form errors: {form.errors}")  # Debug info
    else:
        # Pre-fill service if selected from services page
        initial_data = {}
        if selected_service:
            # Validate that the service is valid
            valid_services = ['recording', 'mixing', 'mastering', 'production', 'vocal_cleanup', 'vocal_tuning', 'hourly', 'daily']
            if selected_service in valid_services:
                initial_data['service'] = selected_service
                print(f"Pre-filling service: {selected_service}")  # Debug info
                print(f"Initial data: {initial_data}")  # Debug info
            else:
                print(f"Invalid service: {selected_service}")  # Debug info
        form = BookingForm(initial=initial_data)
        print(f"Form initial data: {form.initial}")  # Debug info
        print(f"Form service field value: {form['service'].value()}")  # Debug info
    
    if request.method == 'POST':
        # Get client information
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        if form.is_valid():
            # Check if date is available
            if not StudioSchedule.is_date_available(form.cleaned_data['date']):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'This date is not available for booking. Please select another date.'
                    })
                else:
                    messages.error(request, 'This date is not available for booking. Please select another date.')
                    return redirect('booking')
            
            # Check if time slot is available
            time_str = form.cleaned_data['time'].strftime('%H:%M')
            if not TimeSlot.is_time_available(form.cleaned_data['date'], time_str):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'This time slot is not available. Please select another time.'
                    })
                else:
                    messages.error(request, 'This time slot is not available. Please select another time.')
                    return redirect('booking')
            
            # Check for duplicate bookings
            if check_duplicate_booking(
                client_ip,
                form.cleaned_data['email'],
                form.cleaned_data['phone'],
                form.cleaned_data['date'],
                form.cleaned_data['time']
            ):
                # Log duplicate attempt
                SpamLog.objects.create(
                    ip_address=client_ip,
                    user_agent=user_agent,
                    attempt_type='duplicate',
                    details=f'Duplicate booking attempt: {form.cleaned_data["email"]}'
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Duplicate booking detected. Please wait before submitting again.'
                    })
                else:
                    messages.error(request, 'Duplicate booking detected. Please wait before submitting again.')
                    return redirect('booking')
            
            # Save booking with IP information
            booking = form.save(commit=False)
            booking.ip_address = client_ip
            booking.user_agent = user_agent
            booking.save()
            
            # Send email notifications
            try:
                # Send notification to studio
                send_booking_notification_email(booking, request)
                # Send notification to client that request is under review
                send_booking_pending_email(booking, request)
                
                # Clear selected service from session after successful submission
                if 'selected_service' in request.session:
                    del request.session['selected_service']
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Booking request submitted successfully! We will review your request and contact you soon.'
                    })
                else:
                    messages.success(request, 'Booking request submitted successfully! We will review your request and contact you soon.')
                    return redirect('booking')
            except Exception as e:
                # Log the error but don't fail the booking
                print(f"Failed to send email notifications: {e}")
                
                # Clear selected service from session after successful submission
                if 'selected_service' in request.session:
                    del request.session['selected_service']
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Booking request submitted successfully! We will review your request and contact you soon.'
                    })
                else:
                    messages.success(request, 'Booking request submitted successfully! We will review your request and contact you soon.')
                    return redirect('booking')
        else:
            # Handle form validation errors, including reCAPTCHA
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list[0]
                return JsonResponse({
                    'success': False,
                    'message': 'Please fix the errors below.',
                    'errors': errors
                })
            else:
                # Show form errors in messages
                for field, error_list in form.errors.items():
                    if field == 'captcha':
                        messages.error(request, 'Please complete the security check.')
                    else:
                        messages.error(request, f'{field}: {error_list[0]}')
    else:
        form = BookingForm()
    
    # Get available times for today and next 7 days
    available_dates = []
    for i in range(7):
        date = timezone.now().date() + timedelta(days=i)
        if date.weekday() < 5:  # Monday to Friday only
            # Get all time slots with availability status
            all_times = get_all_times_with_status(date.strftime('%Y-%m-%d'))
            if all_times:
                available_dates.append({
                    'date': date,
                    'times': all_times
                })
    
    # Service information
    services_info = {
        'recording': {
            'name': 'Recording',
            'price': '70€/hour',
            'description': 'Professional recording with high-quality equipment'
        },
        'mixing': {
            'name': 'Mixing',
            'price': 'from 200€',
            'description': 'Professional mixing for commercial sound'
        },
        'mastering': {
            'name': 'Mastering',
            'price': '50€/hour',
            'description': 'Loud, clear, and ready for release'
        },
        'production': {
            'name': 'Music Production',
            'price': 'from 400€',
            'description': 'From idea to hit – custom production'
        },
        'vocal_cleanup': {
            'name': 'Vocal Cleanup',
            'price': 'from 100€ to 200€',
            'description': 'Warping and tuning - professional vocal cleanup'
        },
        'vocal_tuning': {
            'name': 'Vocal Tuning',
            'price': '100€/hour',
            'description': 'Perfect pitch, natural feel – Pro vocal tuning'
        },
        'hourly': {
            'name': 'Hourly Rate',
            'price': '70€/hour',
            'description': 'Professional recording and basic processing'
        },
        'daily': {
            'name': 'Daily Rental',
            'price': '450€/day',
            'description': 'Your Studio, Your Time – Full-day rental'
        }
    }
    
    selected_service_info = services_info.get(selected_service, {})
    
    from django.conf import settings as dj_settings
    captcha_enabled = (not dj_settings.DEBUG and bool(dj_settings.RECAPTCHA_PUBLIC_KEY) and bool(dj_settings.RECAPTCHA_PRIVATE_KEY))

    context = {
        'form': form,
        'selected_service': selected_service,
        'selected_service_info': selected_service_info,
        'available_dates': available_dates,
        'captcha_enabled': captcha_enabled,
    }
    
    # Выбор шаблона по языку
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    template_map = {
        'en': 'booking/booking_en.html',
        'ru': 'booking/booking_ru.html',
        'uk': 'booking/booking_uk.html',
        'de': 'booking/booking_de.html',
    }
    template_name = template_map.get(lang, 'booking/booking_en.html')
    seo = {
        'description': _('Book recording, mixing, mastering in Berlin. Choose date and time online.'),
        'keywords': 'book recording berlin, book studio berlin, booking recording studio berlin',
        'og_title': 'Booking – Danov Music Studio Berlin',
        'og_description': _('Online booking of recording sessions in Berlin.'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri('/en/booking/')},
        {'lang': 'ru', 'url': request.build_absolute_uri('/ru/booking/')},
        {'lang': 'uk', 'url': request.build_absolute_uri('/uk/booking/')},
        {'lang': 'de', 'url': request.build_absolute_uri('/de/booking/')},
    ]
    context.update({'seo': seo, 'hreflang_links': hreflang_links, 'hreflang_x_default': request.build_absolute_uri('/booking/')})
    return render(request, template_name, context)


def confirm_booking(request, booking_id):
    """Confirm booking and block the time"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        
        # Send confirmation email to client using new system
        try:
            send_booking_confirmation_email(booking, request)
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")
    
    return HttpResponse(f"""
    <html>
    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
        <h2 style="color: green;">✅ Booking Confirmed!</h2>
        <p>Booking ID #{booking.id} has been confirmed.</p>
        <p>Time slot {booking.time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')} is now blocked.</p>
        <p>Client has been notified via email.</p>
        <button onclick="window.close()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Close</button>
    </body>
    </html>
    """)


def reject_booking(request, booking_id):
    """Reject booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        
        # Send rejection email to client using new system
        try:
            send_booking_rejection_email(booking, request)
        except Exception as e:
            print(f"Failed to send rejection email: {e}")
    
    return HttpResponse(f"""
    <html>
    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
        <h2 style="color: red;">❌ Booking Rejected</h2>
        <p>Booking ID #{booking.id} has been rejected.</p>
        <p>Client has been notified via email.</p>
        <button onclick="window.close()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Close</button>
    </body>
    </html>
    """)


def get_booked_times(date):
    """Get all confirmed booking times for a specific date"""
    confirmed_bookings = Booking.objects.filter(
        date=date,
        status='confirmed'
    )
    
    booked_times = []
    for booking in confirmed_bookings:
        start_time = booking.time
        end_time = (datetime.combine(date, start_time) + timedelta(hours=booking.duration)).time()
        
        # Add all hours in the booking period
        current = datetime.combine(date, start_time)
        end = datetime.combine(date, end_time)
        
        while current < end:
            booked_times.append(current.strftime('%H:%M'))
            current += timedelta(hours=1)
    
    return booked_times


def booking_status(request):
    """Debug page to check booking statuses"""
    bookings = Booking.objects.all().order_by('-created_at')[:10]
    
    context = {
        'bookings': bookings
    }
    
    return render(request, 'booking/booking_status.html', context)


def landing(request, slug: str):
    """Каркас SEO-лендингов под ключевые запросы. Мультиязычный шаблон выбирается по LANGUAGE_CODE."""
    lang = getattr(request, 'LANGUAGE_CODE', 'en') or 'en'
    lang = lang.split('-')[0]
    # Примеры слаги: recording-studio-berlin, mixing-berlin, mastering-berlin, ukrainian-recording-studio-berlin
    template_map = {
        'en': 'booking/landing_en.html',
        'ru': 'booking/landing_ru.html',
        'uk': 'booking/landing_uk.html',
        'de': 'booking/landing_de.html',
    }
    template_name = template_map.get(lang, 'booking/landing_en.html')

    # Сопоставление слогов с ключевой услугой
    slug_to_service = {
        'recording-studio-berlin': 'recording',
        'mixing-berlin': 'mixing',
        'mastering-berlin': 'mastering',
        'music-production-berlin': 'production',
        'vocal-tuning-berlin': 'vocal_tuning',
        'vocal-cleanup-berlin': 'vocal_cleanup',
        'ukrainian-recording-studio-berlin': 'recording',
        # расширения
        'recording-studio-in-berlin': 'recording',
        'best-recording-studio-berlin': 'recording',
        'recording-studio-berlin-prices': 'recording',
        'recording-vocal-studio-berlin': 'recording',
        'mastering-services-berlin': 'mastering',
        'mixing-services-berlin': 'mixing',
        'ukrainian-studio-in-berlin': 'recording',
    }
    service_key = slug_to_service.get(slug, 'recording')

    # Данные услуг по языкам (имя, цена, описание, бенефиты)
    services_i18n = {
        'en': {
            'recording': {
                'name': 'Recording', 'price': '70€/hour', 'desc': 'Record with precision using high-end microphones and treated room.',
                'benefits': ['Professional microphones', 'Acoustic treatment', 'Basic processing', 'Compression and EQ']
            },
            'mixing': {
                'name': 'Mixing', 'price': 'from 200€', 'desc': 'Commercial-ready mix with balance, EQ, compression and effects.',
                'benefits': ['Level balancing', 'Panning', 'EQ and compression', 'Effects and reverb']
            },
            'mastering': {
                'name': 'Mastering', 'price': '50€/hour', 'desc': 'Loud, clear and ready for release on all platforms.',
                'benefits': ['Final EQ', 'Multiband compression', 'Limiting', 'Release prep']
            },
            'production': {
                'name': 'Music Production', 'price': 'from 400€', 'desc': 'From idea to finished track – custom production.',
                'benefits': ['Arrangements', 'Chord progressions', 'Instrumentation', 'Full production']
            },
            'vocal_cleanup': {
                'name': 'Vocal Cleanup', 'price': 'from 100€ to 200€', 'desc': 'Noise/breath cleanup and warping for clean takes.',
                'benefits': ['Noise reduction', 'Vocal tuning', 'Breath control', 'Polishing']
            },
            'vocal_tuning': {
                'name': 'Vocal Tuning', 'price': '100€/hour', 'desc': 'Natural-sounding pitch correction with pro tools.',
                'benefits': ['Pitch correction', 'Natural tuning', 'Melodyne/Auto-Tune', 'Pro results']
            },
        },
        'ru': {
            'recording': {
                'name': 'Запись', 'price': '70€/час', 'desc': 'Точная запись с премиум‑микрофонами и обработанной комнатой.',
                'benefits': ['Профессиональные микрофоны', 'Акустическая обработка', 'Базовая обработка', 'Компрессия и EQ']
            },
            'mixing': {
                'name': 'Сведение', 'price': 'от 200€', 'desc': 'Коммерческий микс: баланс, EQ, компрессия, эффекты.',
                'benefits': ['Баланс уровней', 'Панорама', 'EQ и компрессия', 'Эффекты и реверберация']
            },
            'mastering': {
                'name': 'Мастеринг', 'price': '50€/час', 'desc': 'Громко, чисто и готово к релизу на платформах.',
                'benefits': ['Финальный EQ', 'Мультибэнд‑компрессия', 'Лимитирование', 'Подготовка к релизу']
            },
            'production': {
                'name': 'Продакшн', 'price': 'от 400€', 'desc': 'От идеи до готового трека — кастомная продакшн‑работа.',
                'benefits': ['Аранжировки', 'Аккордовые последовательности', 'Инструментовка', 'Полный продакшн']
            },
            'vocal_cleanup': {
                'name': 'Vocal Cleanup', 'price': 'от 100€ до 200€', 'desc': 'Шумы/дыхание, варпинг — чистый вокал.',
                'benefits': ['Шумоподавление', 'Тюнинг вокала', 'Контроль дыхания', 'Финальный полиш']
            },
            'vocal_tuning': {
                'name': 'Тюнинг вокала', 'price': '100€/час', 'desc': 'Натуральная коррекция интонации проф. инструментами.',
                'benefits': ['Pitch‑коррекция', 'Натуральный тюнинг', 'Melodyne/Auto‑Tune', 'Проф. результат']
            },
        },
        'uk': {
            'recording': {
                'name': 'Запис', 'price': '70€/год', 'desc': 'Точний запис з преміум мікрофонами та обробленою кімнатою.',
                'benefits': ['Професійні мікрофони', 'Акустична обробка', 'Базова обробка', 'Компресія та EQ']
            },
            'mixing': {
                'name': 'Зведення', 'price': 'від 200€', 'desc': 'Комерційний мікс: баланс, EQ, компресія, ефекти.',
                'benefits': ['Баланс рівнів', 'Панорама', 'EQ та компресія', 'Ефекти та реверберація']
            },
            'mastering': {
                'name': 'Мастеринг', 'price': '50€/год', 'desc': 'Гучно, чисто і готово до релізу на платформах.',
                'benefits': ['Фінальний EQ', 'Мультибенд‑компресія', 'Лімітування', 'Підготовка до релізу']
            },
            'production': {
                'name': 'Музичний продакшн', 'price': 'від 400€', 'desc': 'Від ідеї до готового треку — кастомний продакшн.',
                'benefits': ['Аранжування', 'Гармонії', 'Інструментовка', 'Повний продакшн']
            },
            'vocal_cleanup': {
                'name': 'Vocal Cleanup', 'price': 'від 100€ до 200€', 'desc': 'Прибирання шумів/дихання та варпінг для чистого вокалу.',
                'benefits': ['Шумозниження', 'Тюнінг вокалу', 'Контроль дихання', 'Фінальний поліш']
            },
            'vocal_tuning': {
                'name': 'Тюнінг вокалу', 'price': '100€/год', 'desc': 'Натуральна корекція висоти звуку професійними інструментами.',
                'benefits': ['Pitch‑корекція', 'Натуральний тюнінг', 'Melodyne/Auto‑Tune', 'Проф. результат']
            },
        },
        'de': {
            'recording': {
                'name': 'Recording', 'price': '70€/Stunde', 'desc': 'Präzise Aufnahme mit High‑End Mikrofonen und Raumakustik.',
                'benefits': ['Profi‑Mikrofone', 'Akustikbehandlung', 'Basis‑Bearbeitung', 'Kompression und EQ']
            },
            'mixing': {
                'name': 'Mixing', 'price': 'ab 200€', 'desc': 'Release‑fertiger Mix: Balance, EQ, Kompression, Effekte.',
                'benefits': ['Pegel‑Balance', 'Panorama', 'EQ und Kompression', 'Effekte und Hall']
            },
            'mastering': {
                'name': 'Mastering', 'price': '50€/Stunde', 'desc': 'Laut, klar und bereit für den Release.',
                'benefits': ['Finales EQ', 'Multiband‑Kompression', 'Limiting', 'Release‑Vorbereitung']
            },
            'production': {
                'name': 'Music Production', 'price': 'ab 400€', 'desc': 'Von der Idee zum fertigen Track – individuelle Produktion.',
                'benefits': ['Arrangements', 'Harmonien', 'Instrumentation', 'Full Production']
            },
            'vocal_cleanup': {
                'name': 'Vocal Cleanup', 'price': 'ab 100€ bis 200€', 'desc': 'Rausch/Atmer‑Cleanup und Warping für saubere Takes.',
                'benefits': ['Rauschminderung', 'Vocal‑Tuning', 'Atmer‑Kontrolle', 'Finaler Polish']
            },
            'vocal_tuning': {
                'name': 'Vocal Tuning', 'price': '100€/Stunde', 'desc': 'Natürlich klingende Tonhöhenkorrektur mit Pro‑Tools.',
                'benefits': ['Pitch‑Korrektur', 'Natürliches Tuning', 'Melodyne/Auto‑Tune', 'Pro‑Ergebnis']
            },
        },
    }

    svc = services_i18n.get(lang, services_i18n['en'])[service_key]

    # Базовые SEO-данные с заострением под slug
    pretty = slug.replace('-', ' ').title()
    seo = {
        'description': _('%(topic)s – professional services in Berlin. Book a session today.') % {'topic': pretty},
        'keywords': f"{slug.replace('-', ' ')}, recording berlin, studio berlin",
        'og_title': f"{pretty} – Danov Music Studio Berlin",
        'og_description': _('Professional audio services in Berlin.'),
    }
    hreflang_links = [
        {'lang': 'en', 'url': request.build_absolute_uri(f'/en/landing/{slug}/')},
        {'lang': 'ru', 'url': request.build_absolute_uri(f'/ru/landing/{slug}/')},
        {'lang': 'uk', 'url': request.build_absolute_uri(f'/uk/landing/{slug}/')},
        {'lang': 'de', 'url': request.build_absolute_uri(f'/de/landing/{slug}/')},
    ]
    return render(request, template_name, {
        'seo': seo,
        'hreflang_links': hreflang_links,
        'hreflang_x_default': request.build_absolute_uri(f'/landing/{slug}/'),
        'slug': slug,
        'service_key': service_key,
        'service_name': svc['name'],
        'service_price': svc['price'],
        'service_desc': svc['desc'],
        'service_benefits': svc['benefits'],
    })

# Error handlers for better security
def error_400(request, exception):
    """Bad Request"""
    security_logger.warning(f'400 Bad Request: {request.path} from {get_client_ip(request)}')
    return render(request, 'booking/errors/400.html', status=400)

def error_403(request, exception):
    """Forbidden"""
    security_logger.warning(f'403 Forbidden: {request.path} from {get_client_ip(request)}')
    return render(request, 'booking/errors/403.html', status=403)

def error_404(request, exception):
    """Not Found"""
    security_logger.warning(f'404 Not Found: {request.path} from {get_client_ip(request)}')
    return render(request, 'booking/errors/404.html', status=404)

def error_500(request):
    """Internal Server Error"""
    security_logger.error(f'500 Internal Server Error: {request.path} from {get_client_ip(request)}')
    return render(request, 'booking/errors/500.html', status=500)
