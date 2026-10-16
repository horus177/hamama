from django.core.mail import send_mail
from django.conf import settings

def send_otp_via_email(email, otp_code):
    subject = 'رمز التحقق الخاص بك - منصة مزرعتي'
    message = f'رمز التحقق الخاص بك هو: {otp_code}\nهذا الرمز صالح لمدة 5 دقائق فقط.'
    email_from = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
    
    send_mail(
        subject,
        message,
        email_from,
        [email],
        fail_silently=False,
    )