# Generated by Django 5.2.1 on 2025-05-20 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_essayquestion_questionresponse_graded_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='image',
            field=models.FileField(blank=True, help_text='Image to display with this choice', null=True, upload_to='choices/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='choice',
            name='image_alt_text',
            field=models.CharField(blank=True, help_text='Alternative text for the image (for accessibility)', max_length=255),
        ),
        migrations.AddField(
            model_name='question',
            name='external_media_url',
            field=models.URLField(blank=True, help_text='URL to external media like videos or diagrams'),
        ),
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.FileField(blank=True, help_text='Image to display with the question', null=True, upload_to='questions/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='question',
            name='image_alt_text',
            field=models.CharField(blank=True, help_text='Alternative text for the image (for accessibility)', max_length=255),
        ),
        migrations.AddField(
            model_name='question',
            name='media_caption',
            field=models.CharField(blank=True, help_text='Caption for the media content', max_length=255),
        ),
    ]
