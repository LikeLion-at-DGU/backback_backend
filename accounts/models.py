from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel
from django.utils.translation import gettext_lazy as _


class Profile(BaseModel):  # 프로필
    TYPE_CHOICES = [
        ("COMMON", _("COMMON")),
        ("DOCIOR", _("DOCTOR")),
        ("TRAINER", _("TRAINER")),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=15)
    intro = models.CharField(max_length=100)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)  # user 유형
    followings = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )


class ProfileReport(ReportBaseModel):
    profile = models.ForeignKey(
        Profile, related_name="profilereports", on_delete=models.CASCADE
    )
