# Generated by Django 5.2.1 on 2025-05-21 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0002_alter_progress_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='qr_scans',
            field=models.JSONField(blank=True, default=dict, help_text='Record of QR code scans by this user'),
        ),
    ]
