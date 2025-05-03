from django.core.management.base import BaseCommand
from apps.ai_tutor.services import ContentIndexingService
from apps.courses.models import Content

class Command(BaseCommand):
    help = 'Index all course content for AI tutor retrieval'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reindexing of all content, even if already indexed',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # Count content items
        total_content = Content.objects.count()
        self.stdout.write(f"Found {total_content} content items to index")
        
        # Index all content
        indexed_count = 0
        skipped_count = 0
        error_count = 0
        
        for content in Content.objects.select_related('module__course').all():
            try:
                if force or not hasattr(content, 'embedding'):
                    ContentIndexingService.index_content(content)
                    indexed_count += 1
                    self.stdout.write(f"Indexed: {content.title} (ID: {content.id})")
                else:
                    skipped_count += 1
                    self.stdout.write(f"Skipped already indexed: {content.title} (ID: {content.id})")
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"Error indexing {content.title} (ID: {content.id}): {str(e)}"))
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f"Indexing complete:"))
        self.stdout.write(f"  - Total content items: {total_content}")
        self.stdout.write(f"  - Newly indexed: {indexed_count}")
        self.stdout.write(f"  - Skipped (already indexed): {skipped_count}")
        self.stdout.write(f"  - Errors: {error_count}")