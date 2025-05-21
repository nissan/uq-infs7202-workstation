from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import QRCode, QRCodeScan, QRCodeBatch


@receiver(post_save, sender=QRCodeScan)
def update_batch_scan_count(sender, instance, created, **kwargs):
    """Update batch scan count when a new scan is created."""
    if created and instance.qr_code.batch:
        batch = instance.qr_code.batch
        batch.scans_count += 1
        batch.save(update_fields=['scans_count'])


@receiver(post_save, sender=QRCode)
def update_batch_code_count(sender, instance, created, **kwargs):
    """Update batch code count when a new QR code is created."""
    if created and instance.batch:
        batch = instance.batch
        batch.codes_count += 1
        batch.save(update_fields=['codes_count'])


@receiver(post_delete, sender=QRCode)
def decrease_batch_code_count(sender, instance, **kwargs):
    """Decrease batch code count when a QR code is deleted."""
    if instance.batch:
        batch = instance.batch
        batch.codes_count = max(0, batch.codes_count - 1)
        batch.save(update_fields=['codes_count'])