# Generated by Django 5.2.1 on 2025-05-20 18:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_question_alter_quiz_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EssayQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='courses.question')),
                ('min_word_count', models.PositiveIntegerField(default=0, help_text='Minimum word count required (0 for no minimum)')),
                ('max_word_count', models.PositiveIntegerField(default=0, help_text='Maximum word count allowed (0 for no maximum)')),
                ('rubric', models.TextField(blank=True, help_text='Grading rubric or guidelines for instructors')),
                ('example_answer', models.TextField(blank=True, help_text='Example of a good answer (visible only to instructors)')),
                ('allow_attachments', models.BooleanField(default=False, help_text='Allow students to upload attachments')),
            ],
            bases=('courses.question',),
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='graded_at',
            field=models.DateTimeField(blank=True, help_text='When the essay was graded', null=True),
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='graded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='graded_responses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='instructor_comment',
            field=models.TextField(blank=True, help_text='Instructor feedback for essay questions'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False'), ('essay', 'Essay')], max_length=20),
        ),
    ]
