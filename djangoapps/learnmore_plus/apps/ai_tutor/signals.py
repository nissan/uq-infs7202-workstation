from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.courses.models import Content
from apps.ai_tutor.services import ContentIndexingService

@receiver(post_save, sender=Content)
def index_content_on_save(sender, instance, created, **kwargs):
    """
    Signal handler to index or update content in the vector database when content is saved.
    """
    # Defer to service to handle the indexing logic
    if instance.content:  # Only index if there's actual content
        ContentIndexingService.index_content(instance)

@receiver(post_delete, sender=Content)
def remove_content_from_index(sender, instance, **kwargs):
    """
    Signal handler to remove content from the vector database when content is deleted.
    """
    # Defer to service to handle the removal logic
    ContentIndexingService.remove_content(instance)