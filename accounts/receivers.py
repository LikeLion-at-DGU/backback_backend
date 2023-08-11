from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from accounts.models import Profile
import string
import random


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance, type="COMMON")
        profile.nickname = nickname_generator()
        profile.save()


def nickname_generator(length=5):
    prefixes = ["울끈이_", "불끈이_"]
    selected_prefix = random.choice(prefixes)
    letters = string.ascii_lowercase
    random_string = "".join(random.choice(letters) for _ in range(5))
    return selected_prefix + random_string


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
