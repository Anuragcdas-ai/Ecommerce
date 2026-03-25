# from django.db.models.signals import post_save
# from django.contrib.auth.models import User
# from django.dispatch import receiver
# from django.core.mail import send_mail
# from django.conf import settings

# @receiver(post_save, sender=User)
# def send_welcome_email(sender, instance, created, **kwargs):
#     """
#     Send welcome email to newly registered users
#     """
#     if created and instance.email:
#         subject = f"Welcome to {settings.SITE_NAME}!"
#         message = f"""
# Hi {instance.get_full_name|default:instance.username},

# Thank you for registering at {settings.SITE_NAME}. Your account has been successfully created.

# You can now login and start shopping!

# Best regards,
# {settings.SITE_NAME} Team
#         """
        
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[instance.email],
#             fail_silently=False,
#         )