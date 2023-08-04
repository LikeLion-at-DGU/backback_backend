from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel
from django.utils.translation import gettext_lazy as _


class Tag(BaseModel):  # 카테고리
    name = models.CharField(max_length=30, null=False, blank=False)


class Post(BaseModel):  # 게시물
    TYPE_CHOICES = [
        ("ORDINARY", _("ORDINARY")),
        ("PRO", _("PRO")),
    ]
    writer = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def get_reaction_count(self):
        return self.reactions.filter(completed__isnull=True).count()


class PostReport(ReportBaseModel):
    post = models.ForeignKey(Post, related_name="postreports", on_delete=models.CASCADE)


def image_upload_path(instance, filename):
    return f"{instance.post.id}/{filename}"


class Postimage(BaseModel):  # 게시물 이미지
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    post = models.ForeignKey(
        Post, related_name="postimages", null=True, on_delete=models.CASCADE
    )


class Completed(BaseModel):  # 오운완 게시물
    writer = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=500)
    image = models.ImageField(upload_to="post/", blank=True, null=True)

    def get_reaction_count(self):
        return self.reactions.filter(post__isnull=True).count()


class CompletedReport(ReportBaseModel):
    completed = models.ForeignKey(
        Completed, related_name="completedreports", on_delete=models.CASCADE
    )


class Comment(BaseModel):
    writer = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    post = models.ForeignKey(Post, null=False, blank=False, on_delete=models.CASCADE)


class CommentReport(ReportBaseModel):
    comment = models.ForeignKey(
        Comment, related_name="commentreports", on_delete=models.CASCADE
    )


class Reaction(BaseModel):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, null=True, related_name="reactions", on_delete=models.CASCADE
    )
    completed = models.ForeignKey(
        Completed, null=True, related_name="reactions", on_delete=models.CASCADE
    )


class Scrap(BaseModel):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, null=True, related_name="scraps", on_delete=models.CASCADE
    )
