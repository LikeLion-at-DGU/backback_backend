# Generated by Django 4.2.3 on 2023-08-11 15:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_profile_type_alter_profilereport_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="completed_cnt",
            field=models.IntegerField(default=0),
        ),
    ]