from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel


def image_upload_path(instance, filename):
    return f"{instance.id}/{filename}"


class Gym(BaseModel):  # 헬스장 홍보
    name = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    square_feet = models.DecimalField(decimal_places=1, max_digits=10)
    machines = models.JSONField()
    longitude = models.DecimalField(decimal_places=10, max_digits=15)
    latitude = models.DecimalField(decimal_places=10, max_digits=15)
    address = models.CharField(max_length=100)
    key = models.CharField(max_length=10)
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)


class GymReport(ReportBaseModel):  # 헬스장 신고
    gym = models.ForeignKey(Gym, related_name="gymreports", on_delete=models.CASCADE)


class Review(BaseModel):  # 헬스장 리뷰
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    writer = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)


class ReviewReport(ReportBaseModel):  # 리뷰 신고
    review = models.ForeignKey(
        Review, related_name="reviewreports", on_delete=models.CASCADE
    )
