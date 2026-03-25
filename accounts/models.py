from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserType(models.TextChoices):
    BUYER = 'buyer', 'Buyer'
    MERCHANT = 'merchant', 'Merchant'
    ADMIN = 'admin', 'Admin'

# models.py — remove MerchantApplication entirely

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.BUYER)
    phone = models.CharField(max_length=20, blank=True)

    # Merchant fields (only essentials)
    company_name = models.CharField(max_length=200, blank=True)
    business_address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    business_phone = models.CharField(max_length=20, blank=True)
    business_email = models.EmailField(blank=True)
    is_verified_merchant = models.BooleanField(default=False)
    merchant_application_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

    def is_merchant(self):
        return self.user_type == UserType.MERCHANT and self.is_verified_merchant

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)






