# Generated by Django 4.2.3 on 2023-08-06 21:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0002_remove_commentreport_content_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="author",
            new_name="writer",
        ),
        migrations.AlterField(
            model_name="post",
            name="content",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="post",
            name="type",
            field=models.CharField(
                choices=[("ORDINARY", "ORDINARY"), ("PRO", "PRO")], max_length=20
            ),
        ),
    ]
