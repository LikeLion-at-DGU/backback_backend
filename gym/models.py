import json
import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import requests
from core.models import ReportBaseModel, BaseModel


def defalt_info():
    {"exercises": [], "machines": [], "certifications": []}


def image_upload_path(instance, filename):
    return f"gym/{instance.id}/{filename}"


def get_location(gym):  # 경도,위도 저장
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + gym.address
    headers = {"Authorization": "KakaoAK 6556fdbf5f3e592092dbd5678bb76f64"}
    api_json = json.loads(str(requests.get(url, headers=headers).text))
    address = api_json["documents"][0]["address"]
    gym.latitude = float(address["y"])
    gym.longitude = float(address["x"])


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
    key = models.CharField(max_length=10, null=True, blank=True, unique=True)
    info = models.JSONField(default=defalt_info)
    image = models.ImageField(upload_to=image_upload_path, null=True, blank=True)


@receiver(post_save, sender=Gym)
def generate_gym(sender, instance, created, **kwargs):
    if created:
        instance.key = "".join(random.choices(string.ascii_letters, k=10))
        get_location(instance)
        instance.save()


class Review(BaseModel):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="reviews")
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)


class GymReport(ReportBaseModel):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="reports")


class ReviewReport(ReportBaseModel):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reports")
