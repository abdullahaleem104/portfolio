from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
import requests
import urllib.parse
import resend
from .models import Project, ContactMessage


# ========================
# BASIC PAGES
# ========================
def home(request):
    return render(request, 'portfolio/index.html')

def about(request):
    return render(request, 'portfolio/about.html')

def projects_view(request):
    projects = Project.objects.filter(is_active=True)
    return render(request, 'portfolio/projects.html', {'projects': projects})

def skills_view(request):
    return render(request, 'portfolio/skills.html')


# ========================
# EMAIL (RESEND ONLY)
# ========================
resend.api_key = settings.RESEND_API_KEY


def send_email_notification(name, email, subject, message):
    try:
        resend.Emails.send({
            "from": "Portfolio <onboarding@resend.dev>",
            "to": [settings.CONTACT_EMAIL],
            "subject": f"Portfolio Contact: {subject} from {name}",
            "html": f"""
                <h2>📩 New Contact Message</h2>
                <p><b>Name:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Subject:</b> {subject}</p>
                <hr>
                <p>{message}</p>
                <p><small>{timezone.now()}</small></p>
            """
        })
        return True

    except Exception as e:
        print("Resend Error:", e)
        return False


# ========================
# WHATSAPP (OPTIONAL)
# ========================
def send_whatsapp_notification(name, email, subject, message):
    try:
        api_key = settings.WHATSAPP_API_KEY
        phone = settings.WHATSAPP_PHONE_NUMBER

        if not api_key or not phone:
            return False

        msg = f"""🔔 NEW MESSAGE

Name: {name}
Email: {email}
Subject: {subject}
Message: {message[:150]}"""

        encoded = urllib.parse.quote(msg)
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded}&apikey={api_key}"

        response = requests.get(url, timeout=10)
        return response.status_code == 200

    except Exception as e:
        print("WhatsApp Error:", e)
        return False


# ========================
# CONTACT FORM
# ========================
@csrf_protect
def contact(request):
    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        # validation
        errors = []
        if not name:
            errors.append("Name required")
        if not email:
            errors.append("Email required")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Invalid email")

        if not subject:
            errors.append("Subject required")
        if not message:
            errors.append("Message required")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'portfolio/contact.html')

        try:
            # save to DB
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            # EMAIL
            email_sent = send_email_notification(name, email, subject, message)

            # WHATSAPP
            whatsapp_sent = send_whatsapp_notification(name, email, subject, message)

            if email_sent or whatsapp_sent:
                messages.success(request, "✓ Message sent successfully!")
            else:
                messages.warning(request, "Saved but notification failed")

            return redirect('contact')

        except Exception as e:
            print("Contact Error:", e)
            messages.error(request, "Server error, try again later")
            return render(request, 'portfolio/contact.html')

    return render(request, 'portfolio/contact.html')