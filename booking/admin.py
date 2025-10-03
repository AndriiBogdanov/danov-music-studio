from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import Booking, IPTracker, SpamLog, StudioSchedule, TimeSlot, SiteSEOSettings, PageSEO


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'service_display', 'date', 'time', 'duration', 'status', 'status_display', 'ip_address', 'is_suspicious', 'email_sent', 'created_at']
    list_filter = ['service', 'status', 'date', 'created_at', 'is_suspicious']
    search_fields = ['name', 'email', 'phone', 'ip_address']
    readonly_fields = ['created_at', 'ip_address', 'user_agent', 'email_sent', 'email_sent_at', 'confirmation_token', 'rejection_token']
    list_editable = ['status', 'is_suspicious']
    list_per_page = 25  # Show 25 bookings per page
    ordering = ['-created_at']  # Most recent bookings first
    
    def get_queryset(self, request):
        """Force ordering by created_at descending"""
        return super().get_queryset(request).order_by('-created_at')
    
    def service_display(self, obj):
        """Display service with price information"""
        service_prices = {
            'recording': '75€/hour',
            'mixing': 'from 200€',
            'mastering': '50€/hour',
            'production': 'from 400€',
            'vocal_cleanup': 'from 100€ to 200€',
            'vocal_tuning': '100€/hour',
            'hourly': '75€/hour',
            'daily': '450€/day',
        }
        service_name = obj.get_service_display()
        price = service_prices.get(obj.service, '')
        return f"{service_name} ({price})" if price else service_name
    service_display.short_description = "Service"
    
    def status_display(self, obj):
        """Display status with color coding"""
        if obj.status == 'confirmed':
            return format_html('<span style="color: green; font-weight: bold;">✅ CONFIRMED</span>')
        elif obj.status == 'cancelled':
            return format_html('<span style="color: red; font-weight: bold;">❌ CANCELLED</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">⏳ PENDING</span>')
    status_display.short_description = "Status"
    
    fieldsets = (
        ('Client Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Booking Details', {
            'fields': ('service', 'date', 'time', 'duration', 'message'),
            'description': 'Service information and booking details'
        }),
        ('Status & Security', {
            'fields': ('status', 'is_suspicious', 'spam_score', 'created_at')
        }),
        ('Technical Info', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Email System', {
            'fields': ('email_sent', 'email_sent_at', 'confirmation_token', 'rejection_token'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_suspicious', 'mark_as_safe', 'block_ip', 'block_date', 'block_time_slot', 'mark_as_confirmed', 'mark_as_cancelled', 'delete_selected_bookings']
    
    def mark_as_suspicious(self, request, queryset):
        queryset.update(is_suspicious=True)
        self.message_user(request, f"{queryset.count()} bookings marked as suspicious")
    mark_as_suspicious.short_description = "Mark selected bookings as suspicious"
    
    def mark_as_safe(self, request, queryset):
        queryset.update(is_suspicious=False)
        self.message_user(request, f"{queryset.count()} bookings marked as safe")
    mark_as_safe.short_description = "Mark selected bookings as safe"
    
    def block_ip(self, request, queryset):
        ips_blocked = 0
        for booking in queryset:
            if booking.ip_address:
                ip_tracker, created = IPTracker.objects.get_or_create(
                    ip_address=booking.ip_address,
                    defaults={'booking_count': 0, 'is_blocked': False}
                )
                if not ip_tracker.is_blocked:
                    ip_tracker.is_blocked = True
                    ip_tracker.block_reason = "Manually blocked from admin"
                    ip_tracker.save()
                    ips_blocked += 1
        
        self.message_user(request, f"{ips_blocked} IP addresses blocked")
    block_ip.short_description = "Block IP addresses of selected bookings"
    
    def block_date(self, request, queryset):
        dates_blocked = 0
        for booking in queryset:
            schedule, created = StudioSchedule.objects.get_or_create(
                date=booking.date,
                defaults={'is_blocked': True, 'reason': f"Blocked due to booking: {booking.name}"}
            )
            if not schedule.is_blocked:
                schedule.is_blocked = True
                schedule.reason = f"Blocked due to booking: {booking.name}"
                schedule.save()
                dates_blocked += 1
        
        self.message_user(request, f"{dates_blocked} dates blocked")
    block_date.short_description = "Block dates of selected bookings"
    
    def block_time_slot(self, request, queryset):
        slots_blocked = 0
        for booking in queryset:
            slot, created = TimeSlot.objects.get_or_create(
                date=booking.date,
                time=booking.time.strftime('%H:%M'),
                defaults={'is_blocked': True, 'reason': f"Blocked due to booking: {booking.name}"}
            )
            if not slot.is_blocked:
                slot.is_blocked = True
                slot.reason = f"Blocked due to booking: {booking.name}"
                slot.save()
                slots_blocked += 1
        
        self.message_user(request, f"{slots_blocked} time slots blocked")
    block_time_slot.short_description = "Block time slots of selected bookings"

    def mark_as_confirmed(self, request, queryset):
        from .utils import send_booking_confirmation_email
        
        confirmed_count = 0
        for booking in queryset:
            if booking.status != 'confirmed':
                booking.status = 'confirmed'
                booking.save()
                try:
                    send_booking_confirmation_email(booking, request)
                    confirmed_count += 1
                except Exception as e:
                    print(f"Failed to send confirmation email to {booking.email}: {e}")
        
        self.message_user(request, f"{confirmed_count} bookings confirmed and confirmation emails sent")
    mark_as_confirmed.short_description = "Mark selected bookings as confirmed"
    
    def mark_as_cancelled(self, request, queryset):
        from .utils import send_booking_rejection_email
        
        cancelled_count = 0
        for booking in queryset:
            if booking.status != 'cancelled':
                booking.status = 'cancelled'
                booking.save()
                try:
                    send_booking_rejection_email(booking, request)
                    cancelled_count += 1
                except Exception as e:
                    print(f"Failed to send rejection email to {booking.email}: {e}")
        
        self.message_user(request, f"{cancelled_count} bookings cancelled and rejection emails sent")
    mark_as_cancelled.short_description = "Mark selected bookings as cancelled"
    
    def delete_selected_bookings(self, request, queryset):
        """Delete selected bookings and free up time slots"""
        if request.POST.get('post') == 'yes':
            # User confirmed deletion
            deleted_count = 0
            for booking in queryset:
                try:
                    # This will trigger the delete method in the model which frees up time slots
                    booking.delete()
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete booking {booking.id}: {e}")
            
            self.message_user(request, f"{deleted_count} bookings deleted successfully")
            return None
        else:
            # Show confirmation page
            return self.delete_confirmation(request, queryset)
    delete_selected_bookings.short_description = "Delete selected bookings"
    
    def delete_confirmation(self, request, queryset):
        """Show confirmation page for deletion"""
        from django.contrib.admin.actions import delete_selected as delete_selected_action
        return delete_selected_action(self, request, queryset)
    
    def save_model(self, request, obj, form, change):
        """Override save_model to send email notifications when status changes"""
        if change:  # This is an update, not a new booking
            try:
                # Get the original object from database
                original_obj = Booking.objects.get(pk=obj.pk)
                original_status = original_obj.status
                
                # Save the object first
                super().save_model(request, obj, form, change)
                
                # Check if status changed and send email
                if obj.status != original_status:
                    print(f"Status changed from {original_status} to {obj.status} for booking {obj.id}")
                    from .utils import send_booking_confirmation_email, send_booking_rejection_email
                    
                    if obj.status == 'confirmed':
                        print(f"Admin: Sending confirmation email for booking {obj.id} to {obj.email}")
                        try:
                            result = send_booking_confirmation_email(obj, request)
                            if result:
                                self.message_user(request, f"Booking confirmed and confirmation email sent to {obj.email}")
                            else:
                                self.message_user(request, f"Booking confirmed but failed to send email to {obj.email}")
                        except Exception as e:
                            print(f"Error sending confirmation email: {e}")
                            self.message_user(request, f"Booking confirmed but email error: {e}")
                    elif obj.status == 'cancelled':
                        print(f"Admin: Sending rejection email for booking {obj.id} to {obj.email}")
                        try:
                            result = send_booking_rejection_email(obj, request)
                            if result:
                                self.message_user(request, f"Booking cancelled and rejection email sent to {obj.email}")
                            else:
                                self.message_user(request, f"Booking cancelled but failed to send email to {obj.email}")
                        except Exception as e:
                            print(f"Error sending rejection email: {e}")
                            self.message_user(request, f"Booking cancelled but email error: {e}")
                else:
                    print(f"Status didn't change for booking {obj.id}")
                    # Status didn't change, just save normally
                    super().save_model(request, obj, form, change)
                    
            except Booking.DoesNotExist:
                # New booking, save normally
                super().save_model(request, obj, form, change)
            except Exception as e:
                print(f"Error in save_model: {e}")
                # Save anyway, but don't send email
                super().save_model(request, obj, form, change)
        else:
            # New booking, save normally
            super().save_model(request, obj, form, change)


@admin.register(IPTracker)
class IPTrackerAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'booking_count', 'is_blocked', 'block_reason', 'first_seen', 'last_seen']
    list_filter = ['is_blocked', 'first_seen', 'last_seen']
    search_fields = ['ip_address', 'block_reason']
    readonly_fields = ['first_seen', 'last_seen', 'booking_count']
    list_editable = ['is_blocked']
    
    fieldsets = (
        ('IP Information', {
            'fields': ('ip_address', 'booking_count', 'first_seen', 'last_seen')
        }),
        ('Blocking', {
            'fields': ('is_blocked', 'block_reason')
        }),
    )
    
    actions = ['block_selected_ips', 'unblock_selected_ips']
    
    def block_selected_ips(self, request, queryset):
        count = queryset.update(is_blocked=True, block_reason="Manually blocked")
        self.message_user(request, f"{count} IP addresses blocked")
    block_selected_ips.short_description = "Block selected IP addresses"
    
    def unblock_selected_ips(self, request, queryset):
        count = queryset.update(is_blocked=False, block_reason="")
        self.message_user(request, f"{count} IP addresses unblocked")
    unblock_selected_ips.short_description = "Unblock selected IP addresses"


@admin.register(SpamLog)
class SpamLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'attempt_type', 'timestamp', 'details_short']
    list_filter = ['attempt_type', 'timestamp']
    search_fields = ['ip_address', 'details']
    readonly_fields = ['ip_address', 'user_agent', 'attempt_type', 'details', 'timestamp']
    
    def details_short(self, obj):
        """Show shortened details"""
        return obj.details[:50] + "..." if len(obj.details) > 50 else obj.details
    details_short.short_description = "Details"
    
    def has_add_permission(self, request):
        """Disable adding spam logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing spam logs"""
        return False


@admin.register(StudioSchedule)
class StudioScheduleAdmin(admin.ModelAdmin):
    list_display = ['date', 'is_blocked', 'is_holiday', 'is_maintenance', 'status_display', 'reason_short', 'created_at']
    list_filter = ['is_blocked', 'is_holiday', 'is_maintenance', 'date']
    search_fields = ['date', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_blocked', 'is_holiday', 'is_maintenance']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Date Information', {
            'fields': ('date', 'is_blocked', 'is_holiday', 'is_maintenance')
        }),
        ('Details', {
            'fields': ('reason',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['block_selected_dates', 'unblock_selected_dates', 'mark_as_holiday', 'mark_as_maintenance']
    
    def status_display(self, obj):
        if obj.is_blocked:
            if obj.is_holiday:
                return format_html('<span style="color: red;">🚫 HOLIDAY</span>')
            elif obj.is_maintenance:
                return format_html('<span style="color: orange;">🔧 MAINTENANCE</span>')
            else:
                return format_html('<span style="color: red;">🚫 BLOCKED</span>')
        else:
            return format_html('<span style="color: green;">✅ AVAILABLE</span>')
    status_display.short_description = "Status"
    
    def reason_short(self, obj):
        return obj.reason[:30] + "..." if len(obj.reason) > 30 else obj.reason
    reason_short.short_description = "Reason"
    
    def block_selected_dates(self, request, queryset):
        count = queryset.update(is_blocked=True)
        self.message_user(request, f"{count} dates blocked")
    block_selected_dates.short_description = "Block selected dates"
    
    def unblock_selected_dates(self, request, queryset):
        count = queryset.update(is_blocked=False, is_holiday=False, is_maintenance=False, reason="")
        self.message_user(request, f"{count} dates unblocked")
    unblock_selected_dates.short_description = "Unblock selected dates"
    
    def mark_as_holiday(self, request, queryset):
        count = queryset.update(is_blocked=True, is_holiday=True, is_maintenance=False)
        self.message_user(request, f"{count} dates marked as holidays")
    mark_as_holiday.short_description = "Mark selected dates as holidays"
    
    def mark_as_maintenance(self, request, queryset):
        count = queryset.update(is_blocked=True, is_holiday=False, is_maintenance=True)
        self.message_user(request, f"{count} dates marked as maintenance")
    mark_as_maintenance.short_description = "Mark selected dates as maintenance"


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'time', 'is_blocked', 'status_display', 'booking_link', 'reason_short', 'created_at']
    list_filter = ['is_blocked', 'is_booked', 'date', 'time']
    search_fields = ['date', 'time', 'reason']
    readonly_fields = ['created_at', 'booking']
    list_editable = ['is_blocked']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Time Slot Information', {
            'fields': ('date', 'time', 'is_blocked', 'is_booked')
        }),
        ('Booking', {
            'fields': ('booking',)
        }),
        ('Details', {
            'fields': ('reason',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['block_selected_slots', 'unblock_selected_slots']
    
    def status_display(self, obj):
        if obj.is_blocked:
            return format_html('<span style="color: red;">🚫 BLOCKED</span>')
        elif obj.is_booked:
            return format_html('<span style="color: blue;">📅 BOOKED</span>')
        else:
            return format_html('<span style="color: green;">✅ AVAILABLE</span>')
    status_display.short_description = "Status"
    
    def booking_link(self, obj):
        if obj.booking:
            url = reverse('admin:booking_booking_change', args=[obj.booking.id])
            return format_html('<a href="{}">{}</a>', url, obj.booking.name)
        return "-"
    booking_link.short_description = "Booking"
    
    def reason_short(self, obj):
        return obj.reason[:30] + "..." if len(obj.reason) > 30 else obj.reason
    reason_short.short_description = "Reason"
    
    def block_selected_slots(self, request, queryset):
        count = queryset.update(is_blocked=True)
        self.message_user(request, f"{count} time slots blocked")
    block_selected_slots.short_description = "Block selected time slots"
    
    def unblock_selected_slots(self, request, queryset):
        count = queryset.update(is_blocked=False, reason="")
        self.message_user(request, f"{count} time slots unblocked")
    unblock_selected_slots.short_description = "Unblock selected time slots"


@admin.register(SiteSEOSettings)
class SiteSEOSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'gtag_enabled', 'ga4_measurement_id')
    fieldsets = (
        ('Defaults', {
            'fields': ('default_description', 'default_keywords', 'og_image_url')
        }),
        ('Verification', {
            'fields': ('google_site_verification', 'bing_site_verification')
        }),
        ('Social Links', {
            'fields': ('instagram_url', 'youtube_url', 'telegram_url', 'tiktok_url')
        }),
        ('Analytics', {
            'fields': ('gtag_enabled', 'ga4_measurement_id')
        }),
    )

    def has_add_permission(self, request):
        # Единственная запись глобальных настроек
        return not SiteSEOSettings.objects.exists()


@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = ('path', 'language', 'title')
    list_filter = ('language',)
    search_fields = ('path', 'title', 'description', 'keywords')
