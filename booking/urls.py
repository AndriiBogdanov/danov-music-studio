from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='home'),
    path(_('about/'), views.about, name='about'),
    path(_('services/'), views.services, name='services'),
    path(_('equipment/'), views.equipment, name='equipment'),
    path(_('gallery/'), views.gallery, name='gallery'),
    path(_('portfolio/'), views.portfolio, name='portfolio'),
    path(_('contact/'), views.contact, name='contact'),
    path(_('booking/'), views.booking_view, name='booking'),
    path(_('artists/'), views.artists, name='artists'),
    path(_('faq/'), views.faq, name='faq'),
    # SEO Landing pages
    path('landing/<slug:slug>/', views.landing, name='landing'),
    # Booking management
    path('confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path(_('booking-status/'), views.booking_status, name='booking_status'),
]