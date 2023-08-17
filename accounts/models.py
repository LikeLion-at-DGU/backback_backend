from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel
from django.utils.translation import gettext_lazy as _


class Profile(BaseModel):
    TYPE_CHOICES = [
        ("COMMON", _("COMMON")),
        ("DOCTOR", _("DOCTOR")),
        ("TRAINER", _("TRAINER")),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    intro = models.CharField(max_length=100, blank=True)
    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    nickname = models.CharField(max_length=15)
    info = models.JSONField(default={})
    completed_cnt = models.IntegerField(default=0)

    @property
    def level(self):
        level = self.completed_cnt // 3 + 1
        level = 5 if (level > 5) else level
        return level


class ProfileReport(ReportBaseModel):
    profile = models.ForeignKey(
        Profile, related_name="reports", on_delete=models.CASCADE
    )
