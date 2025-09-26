from django.db import models
from django.utils import timezone

class Booking(models.Model):
    SERVICE_CHOICES = [
        ('recording', 'Recording'),
        ('mixing', 'Mixing'),
        ('mastering', 'Mastering'),
        ('production', 'Music Production'),
        ('vocal_cleanup', 'Vocal Cleanup'),
        ('vocal_tuning', 'Vocal Tuning'),
        ('hourly', 'Hourly Rate'),
        ('daily', 'Daily Rental'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, verbose_name="Service")
    date = models.DateField(verbose_name="Date")
    time = models.TimeField(verbose_name="Time")
    duration = models.IntegerField(choices=[
        (1, '1 hour'),
        (2, '2 hours'),
        (3, '3 hours'),
        (4, '4 hours'),
        (5, '5 hours'),
        (6, '6 hours'),
    ], default=1, verbose_name="Duration")
    message = models.TextField(blank=True, verbose_name="Message")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created at")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # Anti-spam fields
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    is_suspicious = models.BooleanField(default=False, verbose_name="Suspicious Activity")
    spam_score = models.IntegerField(default=0, verbose_name="Spam Score")
    
    # Email confirmation fields
    confirmation_token = models.CharField(max_length=100, blank=True, verbose_name="Confirmation Token")
    rejection_token = models.CharField(max_length=100, blank=True, verbose_name="Rejection Token")
    email_sent = models.BooleanField(default=False, verbose_name="Email Sent")
    email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Email Sent At")
    
    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
    
    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"

    @property
    def end_time(self):
        """Calculate the end time based on duration"""
        from datetime import timedelta
        from django.utils import timezone
        start_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        end_datetime = start_datetime + timedelta(hours=self.duration)
        return end_datetime.time()

    def save(self, *args, **kwargs):
        # Check if this is an update and status changed
        status_changed = False
        old_status = None
        
        if self.pk:  # This is an update
            try:
                old_instance = Booking.objects.get(pk=self.pk)
                old_status = old_instance.status
                if self.status != old_status:
                    status_changed = True
            except Booking.DoesNotExist:
                pass
        
        # Save the booking first
        super().save(*args, **kwargs)
        
        # Handle time slot management based on booking status
        if self.pk:  # Only for saved bookings
            time_str = self.time.strftime('%H:%M')
            
            if self.status == 'confirmed':
                # Block time slot for confirmed bookings
                TimeSlot.objects.get_or_create(
                    date=self.date,
                    time=time_str,
                    defaults={
                        'is_booked': True,
                        'booking': self,
                        'reason': f"Booked by {self.name}"
                    }
                )
            else:
                # For pending/cancelled bookings, don't block the time slot
                # Remove any existing time slot if status changed from confirmed to pending/cancelled
                try:
                    existing_slot = TimeSlot.objects.get(date=self.date, time=time_str, booking=self)
                    existing_slot.is_booked = False
                    existing_slot.booking = None
                    existing_slot.reason = ""
                    existing_slot.save()
                except TimeSlot.DoesNotExist:
                    pass
        
        # Send email notifications if status changed
        if status_changed:
            try:
                from .utils import send_booking_confirmation_email, send_booking_rejection_email
                
                if self.status == 'confirmed':
                    print(f"Sending confirmation email for booking {self.id}")
                    send_booking_confirmation_email(self, None)
                elif self.status == 'cancelled':
                    print(f"Sending rejection email for booking {self.id}")
                    send_booking_rejection_email(self, None)
            except Exception as e:
                print(f"Failed to send status change email: {e}")
    
    def delete(self, *args, **kwargs):
        # Free up time slots when booking is deleted
        time_str = self.time.strftime('%H:%M')
        try:
            slot = TimeSlot.objects.get(date=self.date, time=time_str, booking=self)
            slot.is_booked = False
            slot.booking = None
            slot.reason = ""
            slot.save()
        except TimeSlot.DoesNotExist:
            pass
        super().delete(*args, **kwargs)


class IPTracker(models.Model):
    """Model for tracking IP addresses and their activity"""
    ip_address = models.GenericIPAddressField(unique=True, verbose_name="IP Address")
    first_seen = models.DateTimeField(auto_now_add=True, verbose_name="First Seen")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="Last Seen")
    booking_count = models.IntegerField(default=0, verbose_name="Booking Count")
    is_blocked = models.BooleanField(default=False, verbose_name="Is Blocked")
    block_reason = models.CharField(max_length=255, blank=True, verbose_name="Block Reason")
    
    class Meta:
        verbose_name = "IP Tracker"
        verbose_name_plural = "IP Trackers"
        ordering = ['-last_seen']
    
    def __str__(self):
        return f"{self.ip_address} - {self.booking_count} bookings"
    
    def increment_booking_count(self):
        """Increment booking count and check for spam"""
        self.booking_count += 1
        
        # Check for spam patterns
        if self.booking_count > 5:  # More than 5 bookings
            self.is_blocked = True
            self.block_reason = "Too many bookings"
        
        self.save()
    
    def is_rate_limited(self):
        """Check if IP is rate limited (more than 3 bookings in last hour)"""
        from datetime import timedelta
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_bookings = Booking.objects.filter(
            ip_address=self.ip_address,
            created_at__gte=one_hour_ago
        ).count()
        
        return recent_bookings >= 3


class SpamLog(models.Model):
    """Model for logging spam attempts"""
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    attempt_type = models.CharField(max_length=50, choices=[
        ('rate_limit', 'Rate Limited'),
        ('duplicate', 'Duplicate Booking'),
        ('honeypot', 'Honeypot Triggered'),
        ('suspicious', 'Suspicious Activity'),
    ], verbose_name="Attempt Type")
    details = models.TextField(blank=True, verbose_name="Details")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    
    class Meta:
        verbose_name = "Spam Log"
        verbose_name_plural = "Spam Logs"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.ip_address} - {self.attempt_type} - {self.timestamp}"


class StudioSchedule(models.Model):
    """Model for managing studio availability and blocked dates"""
    date = models.DateField(unique=True, verbose_name="Date")
    is_blocked = models.BooleanField(default=False, verbose_name="Blocked Date")
    is_holiday = models.BooleanField(default=False, verbose_name="Holiday")
    is_maintenance = models.BooleanField(default=False, verbose_name="Maintenance Day")
    reason = models.CharField(max_length=255, blank=True, verbose_name="Reason")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    
    class Meta:
        verbose_name = "Studio Schedule"
        verbose_name_plural = "Studio Schedules"
        ordering = ['date']
    
    def __str__(self):
        status = "BLOCKED" if self.is_blocked else "AVAILABLE"
        return f"{self.date} - {status}"
    
    @classmethod
    def is_date_available(cls, date):
        """Check if a date is available for booking"""
        try:
            schedule = cls.objects.get(date=date)
            return not schedule.is_blocked
        except cls.DoesNotExist:
            # If no schedule entry exists, date is available
            return True
    
    @classmethod
    def block_date(cls, date, reason="", is_holiday=False, is_maintenance=False):
        """Block a specific date"""
        schedule, created = cls.objects.get_or_create(
            date=date,
            defaults={
                'is_blocked': True,
                'reason': reason,
                'is_holiday': is_holiday,
                'is_maintenance': is_maintenance
            }
        )
        if not created:
            schedule.is_blocked = True
            schedule.reason = reason
            schedule.is_holiday = is_holiday
            schedule.is_maintenance = is_maintenance
            schedule.save()
        return schedule
    
    @classmethod
    def unblock_date(cls, date):
        """Unblock a specific date"""
        try:
            schedule = cls.objects.get(date=date)
            schedule.is_blocked = False
            schedule.reason = ""
            schedule.is_holiday = False
            schedule.is_maintenance = False
            schedule.save()
            return schedule
        except cls.DoesNotExist:
            return None


class TimeSlot(models.Model):
    """Model for managing specific time slots"""
    TIME_CHOICES = [
        ('09:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM'),
        ('17:00', '5:00 PM'),
        ('18:00', '6:00 PM'),
        ('19:00', '7:00 PM'),
        ('20:00', '8:00 PM'),
        ('21:00', '9:00 PM'),
    ]
    
    date = models.DateField(verbose_name="Date")
    time = models.CharField(max_length=5, choices=TIME_CHOICES, verbose_name="Time")
    is_blocked = models.BooleanField(default=False, verbose_name="Blocked")
    is_booked = models.BooleanField(default=False, verbose_name="Booked")
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Booking")
    reason = models.CharField(max_length=255, blank=True, verbose_name="Reason")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    
    class Meta:
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"
        unique_together = ['date', 'time']
        ordering = ['date', 'time']
    
    def __str__(self):
        status = "BLOCKED" if self.is_blocked else "BOOKED" if self.is_booked else "AVAILABLE"
        return f"{self.date} {self.time} - {status}"
    
    @classmethod
    def is_time_available(cls, date, time):
        """Check if a specific time slot is available"""
        try:
            slot = cls.objects.get(date=date, time=time)
            return not (slot.is_blocked or slot.is_booked)
        except cls.DoesNotExist:
            return True
    
    @classmethod
    def block_time_slot(cls, date, time, reason=""):
        """Block a specific time slot"""
        slot, created = cls.objects.get_or_create(
            date=date,
            time=time,
            defaults={'is_blocked': True, 'reason': reason}
        )
        if not created:
            slot.is_blocked = True
            slot.reason = reason
            slot.save()
        return slot
    
    @classmethod
    def unblock_time_slot(cls, date, time):
        """Unblock a specific time slot"""
        try:
            slot = cls.objects.get(date=date, time=time)
            slot.is_blocked = False
            slot.reason = ""
            slot.save()
            return slot
        except cls.DoesNotExist:
            return None


# --- SEO Models ---
class SiteSEOSettings(models.Model):
    """Глобальные SEO/Analytics настройки (минимальный системный интерфейс)."""
    default_description = models.CharField(max_length=300, blank=True)
    default_keywords = models.CharField(max_length=500, blank=True)
    og_image_url = models.URLField(blank=True)

    # Verification meta tags
    google_site_verification = models.CharField(max_length=200, blank=True)
    bing_site_verification = models.CharField(max_length=200, blank=True)

    # Social links (placeholders до релиза)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    # Analytics (GA4)
    gtag_enabled = models.BooleanField(default=False)
    ga4_measurement_id = models.CharField(max_length=50, blank=True, help_text="G-XXXXXXXXXX")

    def __str__(self) -> str:
        return "Global SEO & Analytics Settings"


class PageSEO(models.Model):
    """SEO-настройки для конкретного пути и языка."""
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('ru', 'Russian'),
        ('uk', 'Ukrainian'),
        ('de', 'German'),
    )

    path = models.CharField(max_length=255, help_text="Абсолютный путь, например /en/services/ или шаблон /services/")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=150, blank=True)
    description = models.CharField(max_length=300, blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.CharField(max_length=300, blank=True)
    og_image_url = models.URLField(blank=True)
    canonical_override = models.URLField(blank=True)

    class Meta:
        unique_together = ('path', 'language')
        indexes = [
            models.Index(fields=['path', 'language']),
        ]

    def __str__(self) -> str:
        return f"SEO {self.language} {self.path}"
