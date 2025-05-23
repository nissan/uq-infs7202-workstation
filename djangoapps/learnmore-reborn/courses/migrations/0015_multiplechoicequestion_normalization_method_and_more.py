# Generated by Django 5.2.1 on 2025-05-20 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_essayquestion_use_detailed_rubric_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='normalization_method',
            field=models.CharField(choices=[('none', 'No Normalization'), ('zscore', 'Z-Score Normalization'), ('minmax', 'Min-Max Scaling'), ('percentile', 'Percentile Ranking'), ('custom', 'Custom Normalization')], default='none', help_text='Method to normalize scores across questions', max_length=20),
        ),
        migrations.AddField(
            model_name='multiplechoicequestion',
            name='normalization_parameters',
            field=models.JSONField(blank=True, default=dict, help_text='Parameters for the normalization method (e.g., {"mean": 0.5, "std_dev": 0.1})'),
        ),
    ]
