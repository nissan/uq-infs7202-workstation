# Generated by Django 5.2 on 2025-05-02 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0005_quiz_is_prerequisite"),
    ]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="is_pre_check",
            field=models.BooleanField(
                default=False,
                help_text="If true, this quiz is a survey/pre-check and not graded",
            ),
        ),
    ]
