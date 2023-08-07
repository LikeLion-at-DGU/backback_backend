from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):  # 생성, 수정 날짜
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ReportBaseModel(BaseModel):  # 신고내용
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50)

    class Meta:
        abstract = True
