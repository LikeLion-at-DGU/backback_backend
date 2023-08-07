from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel


def defalt_info():
    {"exercises": [], "machines": [], "certifications": []}


def image_upload_path(instance, filename):
    return f"gym/{instance.id}/{filename}"


class Gym(BaseModel):
    name = models.CharField(max_length=15)
    square_feet = models.DecimalField(max_digits=10, decimal_places=1)
    latitude = models.DecimalField(
        max_digits=15, decimal_places=10, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=15, decimal_places=10, null=True, blank=True
    )
    address = models.CharField(max_length=100)
    key = models.CharField(max_length=10, null=True, blank=True)
    info = models.JSONField(default=defalt_info)
    image = models.ImageField(upload_to=image_upload_path, null=True, blank=True)


class Review(BaseModel):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="reviews")
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)


class GymReport(ReportBaseModel):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="reports")


class ReviewReport(ReportBaseModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reports")
