from django.db import models
from django.contrib.auth.models import User
from core.models import ReportBaseModel, BaseModel


def image_upload_path(instance, filename):
    return f"{instance.id}/{filename}"
