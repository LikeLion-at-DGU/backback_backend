# Generated by Django 4.2.3 on 2023-08-18 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0012_alter_post_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="exercise",
            field=models.ForeignKey(
                blank=True,
                default="",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to="community.exercise",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="purpose",
            field=models.ForeignKey(
                blank=True,
                default="",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to="community.purpose",
            ),
        ),
    ]