# Generated by Django 4.2.3 on 2023-08-06 21:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gym", "0004_alter_review_gym"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gym",
            name="latitude",
            field=models.DecimalField(decimal_places=10, default=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name="gym",
            name="longitude",
            field=models.DecimalField(decimal_places=10, default=0, max_digits=15),
        ),
    ]
