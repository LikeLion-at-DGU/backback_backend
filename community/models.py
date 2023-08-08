from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel
from django.utils.translation import gettext_lazy as _


class Exercise(BaseModel):
    name = models.CharField(max_length=30, null=False, blank=False)


class Purpose(BaseModel):
    name = models.CharField(max_length=30, null=False, blank=False)


class Post(BaseModel):
    TYPE_CHOICES = [
        ("ORDINARY", _("ORDINARY")),
        ("PRO", _("PRO")),
    ]
    writer = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    exercises = models.ManyToManyField(Exercise, related_name="posts", blank=True)
    purposes = models.ManyToManyField(Purpose, related_name="posts", blank=True)


class PostReport(ReportBaseModel):
    post = models.ForeignKey(Post, related_name="postreports", on_delete=models.CASCADE)


def image_upload_path(instance, filename):
    return f"{instance.post.id}/{filename}"


class PostImage(BaseModel):
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    post = models.ForeignKey(
        Post, related_name="postimages", null=True, on_delete=models.CASCADE
    )


class Scrap(BaseModel):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, null=True, related_name="scraps", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("user", "post")
