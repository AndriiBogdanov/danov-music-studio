from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from .utils import send_booking_confirmation_email, send_booking_rejection_email


@receiver(post_save, sender=Booking)
def booking_status_changed(sender, instance, created, **kwargs):
    """Send email notifications when booking status changes"""
    if not created:  # Only for updates, not new bookings
        try:
            # Check if status changed by comparing with the instance's previous state
            if hasattr(instance, '_state') and hasattr(instance._state, 'fields_cache'):
                # Get the previous status from the instance's state
                old_status = instance._state.fields_cache.get('status', 'pending')
            else:
                # Fallback: get from database
                try:
                    old_instance = Booking.objects.get(pk=instance.pk)
                    old_status = old_instance.status
                except Booking.DoesNotExist:
                    old_status = 'pending'
            
            # Check if status changed
            if instance.status != old_status:
                print(f"Status changed from {old_status} to {instance.status} for booking {instance.id}")
                
                if instance.status == 'confirmed':
                    # Send confirmation email to client
                    send_booking_confirmation_email(instance, None)
                elif instance.status == 'cancelled':
                    # Send rejection email to client
                    send_booking_rejection_email(instance, None)
        except Exception as e:
            print(f"Failed to send status change email: {e}")
