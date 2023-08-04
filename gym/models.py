from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel


class Gym(BaseModel):  # 헬스장 홍보
    name = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    square_feet = models.PositiveIntegerField(default=0)
    machines = models.JSONField()


class GymReport(ReportBaseModel):  # 헬스장 신고
    gym = models.ForeignKey(Gym, related_name="gymreports", on_delete=models.CASCADE)


class Review(BaseModel):  # 헬스장 리뷰
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    writer = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    content = models.TextField()


class ReviewReport(ReportBaseModel):  # 리뷰 신고
    review = models.ForeignKey(
        Review, related_name="reviewreports", on_delete=models.CASCADE
    )
