# Generated by Django 4.2.3 on 2023-08-10 23:32

import community.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0009_completed_is_private"),
    ]

    operations = [
        migrations.CreateModel(
            name="Banner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    models.ImageField(
                        upload_to=community.models.banner_image_upload_path
                    ),
                ),
                ("priority", models.PositiveSmallIntegerField()),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
