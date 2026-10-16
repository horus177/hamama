import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class OTPCode(models.Model):
    PURPOSE_CHOICES = (
        ('VERIFY', 'تأكيد الحساب'),
        ('RESET', 'إعادة تعيين كلمة السر'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='VERIFY')
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        now = timezone.now()
        return not self.is_used and (now - self.created_at) < timedelta(minutes=5)

    @classmethod
    def generate_otp(cls, user, purpose='VERIFY'):
        cls.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
        otp = f"{random.randint(100000, 999999)}"
        return cls.objects.create(user=user, code=otp, purpose=purpose)