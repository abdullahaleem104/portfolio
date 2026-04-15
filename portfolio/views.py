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
        
        if not api_key:
            print("ERROR: RESEND_API_KEY is not configured")
            return False
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "from": "onboarding@resend.dev",
            "to": ["abdullahaleem104@gmail.com"],
            "subject": f"New Message from Portfolio: {subject}",
            "html": f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                        .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; border-radius: 5px; }}
                        .content {{ padding: 20px; }}
                        .field {{ margin-bottom: 15px; }}
                        .label {{ font-weight: bold; color: #4CAF50; }}
                        .message {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 10px; }}
                        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header"><h2>📬 New Contact Form Message</h2></div>
                        <div class="content">
                            <div class="field"><span class="label">👤 Name:</span> {name}</div>
                            <div class="field"><span class="label">📧 Email:</span> <a href="mailto:{email}">{email}</a></div>
                            <div class="field"><span class="label">📋 Subject:</span> {subject}</div>
                            <div class="field"><span class="label">💬 Message:</span>
                            <div class="message">{message}</div></div>
                        </div>
                        <div class="footer">
                            <p>This message was sent from your portfolio website contact form.</p>
                            <p>You can reply directly to: {email}</p>
                        </div>
                    </div>
                </body>
                </html>
            """
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"RESEND STATUS: {response.status_code}")
        print(f"RESEND RESPONSE: {response.text}")
        
        return response.status_code == 200

    except Exception as e:
        print(f"RESEND ERROR: {e}")
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