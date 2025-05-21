from django.core.management.base import BaseCommand
from django.db import transaction
from ai_tutor.models import TutorKnowledgeBase
from ai_tutor.langchain_service import tutor_langchain_service


class Command(BaseCommand):
    help = 'Initialize or update the AI Tutor vector store with knowledge base content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Force recreation of the vector store',
        )

    def handle(self, *args, **options):
        recreate = options['recreate']
        
        # Check if there are knowledge base entries
        kb_count = TutorKnowledgeBase.objects.count()
        if kb_count == 0:
            self.stdout.write(self.style.ERROR(
                "No knowledge base entries found. "
                "Please populate the knowledge base first using populate_knowledge_base command."
            ))
            return
        
        self.stdout.write(self.style.NOTICE(
            f"{'Recreating' if recreate else 'Initializing/updating'} vector store "
            f"with {kb_count} knowledge base entries..."
        ))
        
        try:
            # Process knowledge base and update vector store
            success = tutor_langchain_service.process_knowledge_base(force_recreate=recreate)
            
            if success:
                self.stdout.write(self.style.SUCCESS(
                    f"Vector store successfully {'recreated' if recreate else 'updated'}"
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    "Failed to update vector store. Check logs for details."
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            raise