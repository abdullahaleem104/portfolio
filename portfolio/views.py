from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
import requests
# import resend  ← REMOVED THIS LINE - not needed
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

def send_email_notification(name, email, subject, message):
    """Send email notification using Resend API"""
    try:
        api_key = settings.RESEND_API_KEY
        
        # Debug: Check if API key exists
        if not api_key:
            print("❌ RESEND_API_KEY is not set in settings!")
            return False
        else:
            print(f"✅ RESEND_API_KEY found (length: {len(api_key)})")
            print(f"API Key starts with: {api_key[:10]}...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Create a simpler email first for testing
        email_body = f"""
Name: {name}
Email: {email}
Subject: {subject}
Message: {message}
        """
        
        data = {
            "from": "onboarding@resend.dev",
            "to": ["abdullahaleem104@gmail.com"],  # Your Resend account email
            "subject": f"New Message from Portfolio: {subject}",
            "text": email_body,  # Use plain text first for testing
        }
        
        print(f"📧 Attempting to send email to: abdullahaleem104@gmail.com")
        print(f"📧 From: onboarding@resend.dev")
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📡 Resend Response Status: {response.status_code}")
        print(f"📡 Resend Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Email sent successfully!")
            return True
        else:
            print(f"❌ Resend API error: {response.status_code}")
            print(f"Error details: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Resend API timeout - request took too long")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error to Resend: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def send_whatsapp_notification(name, email, subject, message):
    """Send WhatsApp notification using CallMeBot API"""
    try:
        whatsapp_api_key = getattr(settings, 'WHATSAPP_API_KEY', None)
        phone_number = getattr(settings, 'WHATSAPP_PHONE_NUMBER', None)
        
        if whatsapp_api_key and phone_number:
            import urllib.parse
            whatsapp_msg = f"""🔔 NEW CONTACT FORM MESSAGE!

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
            
            # 2. Send Email via Resend
            email_sent = send_email_notification(name, email, subject, message)
            
            # 3. Send WhatsApp Notification (optional)
            whatsapp_sent = send_whatsapp_notification(name, email, subject, message)
            
            if email_sent:
                messages.success(request, '✓ Thank you! Your message has been sent successfully. I\'ll get back to you soon!')
            elif whatsapp_sent:
                messages.warning(request, 'Your message was saved but email notification failed. I will still receive your message.')
            else:
                messages.warning(request, 'Your message was saved but there was an issue with notifications. I will still review it.')
            
            return redirect('contact')
            
        except Exception as e:
            print(f"Contact form error: {e}")
            messages.error(request, 'An error occurred. Please try again later.')
            return render(request, 'portfolio/contact.html')
    
    return render(request, 'portfolio/contact.html')