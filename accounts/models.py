from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Email preferences
    newsletter_subscription = models.BooleanField(default=False)
    order_updates = models.BooleanField(default=True)
    
    # Account stats
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loyalty_points = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def get_profile_image(self):
        if self.profile_image:
            return self.profile_image.url
        return '/static/images/default-avatar.png'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)#correction not able to get already created User object
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


