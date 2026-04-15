from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
import requests
from .models import Project, ContactMessage


def home(request):
    return render(request, 'portfolio/index.html')


def about(request):
    return render(request, 'portfolio/about.html')


def projects_view(request):
    projects = Project.objects.filter(is_active=True)
    return render(request, 'portfolio/projects.html', {'projects': projects})


def skills_view(request):
    return render(request, 'portfolio/skills.html')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


# ================= EMAIL (SAFE VERSION) =================
def send_email_notification(name, email, subject, message):
    try:
        # 🔥 prevent crash if env not set
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("Email not configured - skipping")
            return False

        full_message = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

Time: {timezone.now()}
"""

        send_mail(
            subject=f'Portfolio Contact: {subject} from {name}',
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=True,  # 🔥 IMPORTANT (prevents 500 error)
        )

        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False


# ================= WHATSAPP (SAFE VERSION) =================
def send_whatsapp_notification(name, email, subject, message):
    try:
        whatsapp_api_key = getattr(settings, 'WHATSAPP_API_KEY', None)
        phone_number = getattr(settings, 'WHATSAPP_PHONE_NUMBER', None)

        # 🔥 skip safely if not configured
        if not whatsapp_api_key or not phone_number:
            print("WhatsApp not configured - skipping")
            return False

        import urllib.parse

        whatsapp_msg = f"""NEW CONTACT MESSAGE

Name: {name}
Email: {email}
Subject: {subject}
Message: {message[:120]}...
"""

        encoded_msg = urllib.parse.quote(whatsapp_msg)

        url = (
            f"https://api.callmebot.com/whatsapp.php"
            f"?phone={phone_number}"
            f"&text={encoded_msg}"
            f"&apikey={whatsapp_api_key}"
        )

        response = requests.get(url, timeout=5)

        return response.status_code == 200

    except Exception as e:
        print(f"WhatsApp error: {e}")
        return False


# ================= CONTACT VIEW =================
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
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Invalid email format')

        if not subject:
            errors.append('Subject is required')

        if not message:
            errors.append('Message is required')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'portfolio/contact.html')

        try:
            # 1. Save to database (ALWAYS SAFE)
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
                ip_address=get_client_ip(request)
            )

            # 2. Email (DO NOT CRASH SITE)
            email_sent = False
            try:
                email_sent = send_email_notification(name, email, subject, message)
            except Exception as e:
                print("Email skipped:", e)

            # 3. WhatsApp (DO NOT CRASH SITE)
            whatsapp_sent = False
            try:
                whatsapp_sent = send_whatsapp_notification(name, email, subject, message)
            except Exception as e:
                print("WhatsApp skipped:", e)

            # 4. User message (always success if saved)
            messages.success(
                request,
                "✓ Message sent successfully! I’ll get back to you soon ❤️"
            )

            return redirect('contact')

        except Exception as e:
            print(f"Contact form error: {e}")
            messages.error(request, "Something went wrong. Please try again later.")
            return render(request, 'portfolio/contact.html')

    return render(request, 'portfolio/contact.html')