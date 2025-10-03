from django import forms
from .models import Booking
from datetime import date, time
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
import re

class BookingForm(forms.ModelForm):
    # Temporarily disabled for testing
    # captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    # Honey pot fields - hidden from real users, but bots might fill them
    # Temporarily disabled for testing
    # website = forms.CharField(required=False, widget=forms.HiddenInput())
    # email_confirmation = forms.CharField(required=False, widget=forms.HiddenInput())
    # phone_backup = forms.CharField(required=False, widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set choices for service field with prices
        self.fields['service'].choices = [
            ('', 'Select a service...'),
            ('recording', 'Recording - 75€/hour'),
            ('mixing', 'Mixing - from 200€'),
            ('mastering', 'Mastering - 50€/hour'),
            ('production', 'Music Production - from 400€'),
            ('vocal_cleanup', 'Vocal Cleanup - from 100€ to 200€'),
            ('vocal_tuning', 'Vocal Tuning - 100€/hour'),
            ('hourly', 'Hourly Rate - 75€/hour'),
            ('daily', 'Daily Rental - 450€/day'),
        ]
    
    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'service', 'date', 'time', 'duration', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+49 175 413 75 18',
                'type': 'text',
                'autocomplete': 'off',
                'data-lpignore': 'true',
                'inputmode': 'tel'
            }),
            'service': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'duration': forms.Select(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional information about your project...'
            })
        }
    
    def clean_date(self):
        date_val = self.cleaned_data.get('date')
        if date_val and date_val < date.today():
            raise forms.ValidationError("Cannot book studio for past dates")
        return date_val
    
    def clean_time(self):
        time_val = self.cleaned_data.get('time')
        if time_val:
            # Check if time is within working hours (9:00 - 21:30)
            if time_val < time(9, 0) or time_val > time(21, 30):
                raise forms.ValidationError("Studio is open from 9:00 AM to 9:30 PM")
        return time_val
    
    # Honey pot validation temporarily disabled for testing
    # def clean_website(self):
    #     """Honey pot field - should be empty"""
    #     website = self.cleaned_data.get('website')
    #     if website:
    #         raise forms.ValidationError("Bot detected - website field should be empty")
    #     return website
    
    # def clean_email_confirmation(self):
    #     """Honey pot field - should be empty"""
    #     email_confirmation = self.cleaned_data.get('email_confirmation')
    #     if email_confirmation:
    #         raise forms.ValidationError("Bot detected - email_confirmation field should be empty")
    #     return email_confirmation
    
    # def clean_phone_backup(self):
    #     """Honey pot field - should be empty"""
    #     phone_backup = self.cleaned_data.get('phone_backup')
    #     if phone_backup:
    #         raise forms.ValidationError("Bot detected - phone_backup field should be empty")
    #     return phone_backup
    
    def clean_name(self):
        """Enhanced name validation"""
        name = self.cleaned_data.get('name')
        if name:
            # Check for suspicious patterns
            if len(name) < 2:
                raise forms.ValidationError("Name must be at least 2 characters long")
            
            # Check for too many numbers
            if sum(c.isdigit() for c in name) > 2:
                raise forms.ValidationError("Name contains too many numbers")
            
            # Check for suspicious keywords (temporarily disabled for testing)
            # suspicious_keywords = ['test', 'spam', 'bot', 'admin', 'null', 'undefined']
            # if any(keyword in name.lower() for keyword in suspicious_keywords):
            #     raise forms.ValidationError("Invalid name")
            
            # Check for excessive special characters
            special_chars = sum(1 for c in name if not c.isalnum() and c not in ' -.,')
            if special_chars > 2:
                raise forms.ValidationError("Name contains too many special characters")
        
        return name
    
    def clean_email(self):
        """Enhanced email validation"""
        email = self.cleaned_data.get('email')
        if email:
            # Check for suspicious email patterns
            suspicious_domains = ['tempmail.', 'guerrillamail.', 'mailinator.', '10minutemail.']
            if any(domain in email.lower() for domain in suspicious_domains):
                raise forms.ValidationError("Temporary email addresses are not allowed")
            
            # Check for multiple @ symbols
            if email.count('@') != 1:
                raise forms.ValidationError("Invalid email format")
            
            # Check for suspicious patterns
            if re.search(r'[0-9]{8,}', email):  # 8+ consecutive digits
                raise forms.ValidationError("Suspicious email pattern")
        
        return email
    
    def clean_service(self):
        """Service validation"""
        service = self.cleaned_data.get('service')
        if not service:
            raise forms.ValidationError("Please select a service")
        return service
    
    def clean_phone(self):
        """Enhanced phone validation"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters for validation
            digits_only = re.sub(r'\D', '', phone)
            
            # Check minimum length
            if len(digits_only) < 10:
                raise forms.ValidationError("Phone number must be at least 10 digits")
            
            # Check maximum length
            if len(digits_only) > 15:
                raise forms.ValidationError("Phone number is too long")
            
            # Check for suspicious patterns (all same digits)
            if len(set(digits_only)) <= 2:
                raise forms.ValidationError("Invalid phone number pattern")
        
        return phone
    
    def clean_message(self):
        """Enhanced message validation"""
        message = self.cleaned_data.get('message')
        if message:
            # Check for suspicious URLs
            if re.search(r'http[s]?://|www\.', message, re.IGNORECASE):
                raise forms.ValidationError("URLs are not allowed in messages")
            
            # Check for excessive special characters
            special_chars = sum(1 for c in message if not c.isalnum() and c not in ' .,!?-\n')
            if special_chars > len(message) * 0.3:  # More than 30% special chars
                raise forms.ValidationError("Message contains too many special characters")
            
            # Check for spam keywords
            spam_keywords = ['viagra', 'casino', 'lottery', 'winner', 'congratulations', 'click here']
            if any(keyword in message.lower() for keyword in spam_keywords):
                raise forms.ValidationError("Message contains prohibited content")
        
        return message
    
    def clean(self):
        """Overall form validation"""
        cleaned_data = super().clean()
        
        # Honey pot validation temporarily disabled for testing
        # # Check if any honey pot field is filled
        # honey_pot_fields = ['website', 'email_confirmation', 'phone_backup']
        # for field in honey_pot_fields:
        #     if cleaned_data.get(field):
        #         raise forms.ValidationError("Spam detected - form submission blocked")
        
        return cleaned_data 