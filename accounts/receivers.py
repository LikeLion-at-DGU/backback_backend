from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from accounts.models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, type="COMMON")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
