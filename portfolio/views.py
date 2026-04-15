from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
import requests
import socket
from .models import Project, ContactMessage

def home(request):
    return render(request, 'portfolio/index.html')

def about(request):
    return render(request, 'portfolio/about.html')

def projects_view(request):
    projects = Project.objects.filter(is_active=True)
    context = {
        'projects': projects
    }
    return render(request, 'portfolio/projects.html', context)

def skills_view(request):
    return render(request, 'portfolio/skills.html')

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

import socket

def send_email_notification(name, email, subject, message):
    try:
        socket.setdefaulttimeout(5)  # 👈 IMPORTANT FIX

        full_message = f"""
        📧 New Contact Form Submission
        
        👤 Name: {name}
        📧 Email: {email}
        📋 Subject: {subject}
        💬 Message:
        {message}
        """

        send_mail(
            subject=f'Portfolio Contact: {subject} from {name}',
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=True,   # 👈 VERY IMPORTANT
        )

        return True

    except Exception as e:
        print("Email error:", e)
        return False
    
def send_whatsapp_notification(name, email, subject, message):
    """Send WhatsApp notification using CallMeBot API"""
    try:
        whatsapp_api_key = getattr(settings, 'WHATSAPP_API_KEY', None)
        phone_number = getattr(settings, 'WHATSAPP_PHONE_NUMBER', None)
        
        if whatsapp_api_key and phone_number:
            # Prepare message (URL encode)
            import urllib.parse
            whatsapp_msg = f"""🔔 NEW CONTACT FORM MESSAGE!🔔

👤 Name: {name}
📧 Email: {email}
📋 Subject: {subject}
💬 Message: {message[:150]}..."""
            
            encoded_msg = urllib.parse.quote(whatsapp_msg)
            url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={encoded_msg}&apikey={whatsapp_api_key}"
            
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        
        return False
        
    except Exception as e:
        print(f"WhatsApp error: {e}")
        return False

@csrf_protect
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validation
        errors = []
        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        elif email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Please enter a valid email address')
        if not subject:
            errors.append('Subject is required')
        if not message:
            errors.append('Message is required')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'portfolio/contact.html')
        
        try:
            # 1. Save to database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
                ip_address=get_client_ip(request)
            )
            
            # 2. Send Email
            email_sent = send_email_notification(name, email, subject, message)
            
            # 3. Send WhatsApp Notification
            whatsapp_sent = send_whatsapp_notification(name, email, subject, message)
            
            if email_sent or whatsapp_sent:
                messages.success(request, '✓ Thank you! Your message has been sent successfully. I\'ll get back to you soon!')
            else:
                messages.warning(request, 'Your message was saved but there was an issue with notifications. I will still receive it via email.')
            
            return redirect('contact')
            
        except Exception as e:
            messages.error(request, f'An error occurred. Please try again later.')
            print(f"Contact form error: {e}")
            return render(request, 'portfolio/contact.html')
    
    return render(request, 'portfolio/contact.html')