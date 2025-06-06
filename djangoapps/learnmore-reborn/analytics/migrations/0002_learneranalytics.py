# Generated by Django 5.2.1 on 2025-05-20 21:25

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LearnerAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_quizzes_taken', models.PositiveIntegerField(default=0)),
                ('total_quizzes_passed', models.PositiveIntegerField(default=0)),
                ('total_questions_answered', models.PositiveIntegerField(default=0)),
                ('total_correct_answers', models.PositiveIntegerField(default=0)),
                ('average_time_per_question', models.FloatField(default=0.0, help_text='Average time in seconds spent per question')),
                ('total_study_time', models.DurationField(default=datetime.timedelta, help_text='Total time spent on learning activities')),
                ('strengths', models.JSONField(blank=True, default=list, help_text='Categories or topics where the learner excels')),
                ('areas_for_improvement', models.JSONField(blank=True, default=list, help_text='Categories or topics where the learner struggles')),
                ('learning_pattern_data', models.JSONField(blank=True, default=dict, help_text='Data about learning patterns like time of day, duration, etc.')),
                ('quiz_performance_history', models.JSONField(blank=True, default=list, help_text='Historical data of quiz performances')),
                ('progress_over_time', models.JSONField(blank=True, default=dict, help_text='Chart data for progress visualization')),
                ('performance_by_category', models.JSONField(blank=True, default=dict, help_text='Performance metrics grouped by question categories')),
                ('course_completion_data', models.JSONField(blank=True, default=dict, help_text='Completion rates and performance by course')),
                ('percentile_ranking', models.JSONField(blank=True, default=dict, help_text='Percentile ranking compared to peers by category')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Learner Analytics',
                'verbose_name_plural': 'Learner Analytics',
            },
        ),
    ]
