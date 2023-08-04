from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):  # 생성, 수정 날짜
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ReportBaseModel(BaseModel):  # 신고내용
    REASON_CHOICES = [
        # 신고 카테고리
    ]
    writer = models.OneToOneField(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=10, choices=REASON_CHOICES)
    content = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True
