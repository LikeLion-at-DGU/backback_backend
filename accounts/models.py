from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(BaseModel):  # 프로필
    TYPE_CHOICES = [
        ("COMMON", _("COMMON")),
        ("DOCIOR", _("DOCTOR")),
        ("TRAINER", _("TRAINER")),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=15)
    intro = models.CharField(max_length=100)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)  # user 유형
    followings = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            profile = Profile.objects.create(user=instance, type="COMMON")

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class ProfileReport(ReportBaseModel):
    profile = models.ForeignKey(
        Profile, related_name="profilereports", on_delete=models.CASCADE
    )
