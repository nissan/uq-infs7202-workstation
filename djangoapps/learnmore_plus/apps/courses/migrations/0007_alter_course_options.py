# Generated by Django 5.2 on 2025-05-02 15:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0006_quiz_is_pre_check"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="course",
            options={
                "ordering": ["-created_at"],
                "permissions": [
                    ("publish_course", "Can publish course"),
                    ("archive_course", "Can archive course"),
                    ("manage_courses", "Can manage courses"),
                    ("manage_enrollments", "Can manage enrollments"),
                    ("create_courses", "Can create courses"),
                    ("manage_modules", "Can manage modules"),
                    ("view_courses", "Can view courses"),
                    ("take_quizzes", "Can take quizzes"),
                ],
            },
        ),
    ]
