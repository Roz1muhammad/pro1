from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random

# ==============================
# Viloyatlar (to‘liq)
# ==============================
REGION_CHOICES = [
    ('tashkent', 'Toshkent'),
    ('samarkand', 'Samarqand'),
    ('bukhara', 'Buxoro'),
    ('fergana', 'Farg‘ona'),
    ('andijan', 'Andijon'),
    ('namangan', 'Namangan'),
    ('sirdaryo', 'Sirdaryo'),
    ('jizzakh', 'Jizzax'),
    ('navoiy', 'Navoiy'),
    ('kashkadaryo', 'Qashqadaryo'),
    ('surxandaryo', 'Surxondaryo'),
    ('xorazm', 'Xorazm'),
    ('qoraqalpogiston', 'Qoraqalpog‘iston'),
]

# ==============================
# USER MODEL
# ==============================
class User(AbstractUser):
    """
    OTP orqali ro‘yxatdan o‘tadigan user modeli
    """

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    region = models.CharField(
        max_length=50,
        choices=REGION_CHOICES,
        null=True,
        blank=True
    )

    birth_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

# ==============================
# OTP MODEL
# ==============================
class Otp(models.Model):
    """
    OTP faqat emailga bog‘lanadi
    3 minut + 3 urinish qo‘llanadi
    """
    email = models.EmailField()
    code = models.CharField(max_length=6, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    tries = models.PositiveSmallIntegerField(default=0)

    def is_expired(self):
        """3 minutdan oshsa OTP expired"""
        return (timezone.now() - self.created).total_seconds() > 180

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} - {self.code}"
