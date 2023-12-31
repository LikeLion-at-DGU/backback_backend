# Generated by Django 4.2.3 on 2023-08-07 21:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gym", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="gym",
            old_name="longiude",
            new_name="longitude",
        ),
        migrations.RemoveField(
            model_name="gym",
            name="machines",
        ),
        migrations.AlterField(
            model_name="gym",
            name="info",
            field=models.JSONField(
                default={"certifications": [], "exercises": [], "machines": []}
            ),
        ),
        migrations.AlterField(
            model_name="gym",
            name="key",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
