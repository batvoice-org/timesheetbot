# Generated by Django 2.2.12 on 2020-05-08 18:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("timesheetbot", "0002_manual_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="slack_republish_hook",
            field=models.CharField(blank=True, default="", max_length=127),
        ),
    ]
