from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel


class Profile(BaseModel):  # 프로필
    TYPE_CHOICES = [
        # 일반
        # 의사
        # 트레이너
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=15)
    intro = models.TextField(max_length=100)  # 자기소개
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)  # user 유형
    followings = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )


class ProfileReport(ReportBaseModel):  # 유저 신고
    profile = models.ForeignKey(
        Profile, related_name="profilereports", on_delete=models.CASCADE
    )
