# Generated by Django 4.2.1 on 2023-08-08 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="postimage",
            name="post",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="community.post",
            ),
        ),
        migrations.AlterField(
            model_name="postreport",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reports",
                to="community.post",
            ),
        ),
    ]
