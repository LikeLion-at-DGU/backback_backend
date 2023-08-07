from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel
from django.utils.translation import gettext_lazy as _


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


class ProfileReport(ReportBaseModel):
    profile = models.ForeignKey(
        Profile, related_name="profilereports", on_delete=models.CASCADE
    )
