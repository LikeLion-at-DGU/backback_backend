from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(BaseModel):
    TYPE_CHOICES = [
        ("COMMON", _("COMMON")),
        ("DOCIOR", _("DOCTOR")),
        ("TRAINER", _("TRAINER")),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    intro = models.CharField(max_length=100)
    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    nickname = models.CharField(max_length=15)
    info = models.JSONField(default="{}")

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class ProfileReport(ReportBaseModel):
    profile = models.ForeignKey(
        Profile, related_name="profilereports", on_delete=models.CASCADE
    )
