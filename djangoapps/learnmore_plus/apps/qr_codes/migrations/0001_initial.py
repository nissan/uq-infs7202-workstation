# Generated by Django 5.2 on 2025-05-03 07:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="QRCode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "code",
                    models.ImageField(blank=True, null=True, upload_to="qr_codes/"),
                ),
                ("url", models.URLField(max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_used", models.DateTimeField(blank=True, null=True)),
                ("scan_count", models.IntegerField(default=0)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="QRCodeScan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scanned_at", models.DateTimeField(auto_now_add=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True, null=True)),
                (
                    "qr_code",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scans",
                        to="qr_codes.qrcode",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="qrcode",
            index=models.Index(
                fields=["content_type", "object_id"],
                name="qr_codes_qr_content_3eeb05_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="qrcode",
            index=models.Index(
                fields=["created_at"], name="qr_codes_qr_created_c405a6_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="qrcode",
            unique_together={("content_type", "object_id")},
        ),
        migrations.AddIndex(
            model_name="qrcodescan",
            index=models.Index(
                fields=["qr_code", "scanned_at"], name="qr_codes_qr_qr_code_5a1cbc_idx"
            ),
        ),
    ]
