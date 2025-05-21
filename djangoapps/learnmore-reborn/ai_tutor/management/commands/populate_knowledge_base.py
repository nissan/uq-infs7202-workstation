import os
import csv
import json
from typing import List, Dict, Any
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from courses.models import Course, Module
from ai_tutor.models import TutorKnowledgeBase
from ai_tutor.langchain_service import tutor_langchain_service


class Command(BaseCommand):
    help = 'Populate the AI Tutor knowledge base and initialize the vector store'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            dest='csv_file',
            help='Path to CSV file with knowledge base content',
        )
        parser.add_argument(
            '--json',
            dest='json_file',
            help='Path to JSON file with knowledge base content',
        )
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Force recreation of the vector store',
        )
        parser.add_argument(
            '--from-modules',
            action='store_true',
            help='Create knowledge base entries from existing course modules',
        )
        parser.add_argument(
            '--skip-vector-store',
            action='store_true',
            help='Skip vector store creation/update',
        )

    def handle(self, *args, **options):
        try:
            # Track statistics
            stats = {
                'created': 0,
                'skipped': 0,
                'errors': 0,
                'vector_store_updated': False,
            }
            
            # Process CSV file if provided
            if options['csv_file']:
                self.stdout.write(self.style.NOTICE(f"Processing CSV file: {options['csv_file']}"))
                stats_csv = self.process_csv_file(options['csv_file'])
                for key in stats:
                    if key in stats_csv:
                        stats[key] += stats_csv[key]
            
            # Process JSON file if provided
            if options['json_file']:
                self.stdout.write(self.style.NOTICE(f"Processing JSON file: {options['json_file']}"))
                stats_json = self.process_json_file(options['json_file'])
                for key in stats:
                    if key in stats_json:
                        stats[key] += stats_json[key]
            
            # Process module content if requested
            if options['from_modules']:
                self.stdout.write(self.style.NOTICE("Creating knowledge base entries from course modules"))
                stats_modules = self.process_modules()
                for key in stats:
                    if key in stats_modules:
                        stats[key] += stats_modules[key]
            
            # Update vector store if not skipped
            if not options['skip_vector_store']:
                recreate = options['recreate']
                self.stdout.write(self.style.NOTICE(
                    f"{'Recreating' if recreate else 'Updating'} vector store"
                ))
                
                success = tutor_langchain_service.process_knowledge_base(force_recreate=recreate)
                if success:
                    self.stdout.write(self.style.SUCCESS("Vector store successfully updated"))
                    stats['vector_store_updated'] = True
                else:
                    self.stdout.write(self.style.ERROR("Failed to update vector store"))
            
            # Print summary
            self.stdout.write("\nKnowledge base population summary:")
            self.stdout.write(f"  - Created: {stats['created']} entries")
            self.stdout.write(f"  - Skipped: {stats['skipped']} entries")
            self.stdout.write(f"  - Errors: {stats['errors']} entries")
            self.stdout.write(f"  - Vector store updated: {stats['vector_store_updated']}")
            
            if stats['created'] > 0:
                self.stdout.write(self.style.SUCCESS("\nKnowledge base populated successfully!"))
            else:
                self.stdout.write(self.style.WARNING("\nNo new knowledge base entries were created."))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            raise
    
    def process_csv_file(self, csv_path: str) -> Dict[str, int]:
        """Process a CSV file containing knowledge base entries."""
        stats = {'created': 0, 'skipped': 0, 'errors': 0}
        
        # Check if file exists
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file does not exist: {csv_path}"))
            return stats
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate required columns
                required_cols = ['title', 'content']
                missing_cols = [col for col in required_cols if col not in reader.fieldnames]
                if missing_cols:
                    self.stdout.write(self.style.ERROR(
                        f"CSV is missing required columns: {', '.join(missing_cols)}"
                    ))
                    return stats
                
                # Process rows
                with transaction.atomic():
                    for row in reader:
                        try:
                            # Get course and module if specified
                            course = None
                            module = None
                            
                            if 'course_id' in row and row['course_id']:
                                try:
                                    course = Course.objects.get(id=int(row['course_id']))
                                except (Course.DoesNotExist, ValueError):
                                    self.stdout.write(self.style.WARNING(
                                        f"Course with ID {row['course_id']} not found"
                                    ))
                            
                            if 'module_id' in row and row['module_id']:
                                try:
                                    module = Module.objects.get(id=int(row['module_id']))
                                except (Module.DoesNotExist, ValueError):
                                    self.stdout.write(self.style.WARNING(
                                        f"Module with ID {row['module_id']} not found"
                                    ))
                            
                            # Check if entry already exists
                            existing = TutorKnowledgeBase.objects.filter(
                                title=row['title'],
                                course=course,
                                module=module
                            ).first()
                            
                            if existing:
                                self.stdout.write(f"Skipping existing entry: {row['title']}")
                                stats['skipped'] += 1
                                continue
                            
                            # Create new entry
                            TutorKnowledgeBase.objects.create(
                                title=row['title'],
                                content=row['content'],
                                course=course,
                                module=module
                            )
                            
                            stats['created'] += 1
                            self.stdout.write(f"Created entry: {row['title']}")
                            
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error processing row: {str(e)}"))
                            stats['errors'] += 1
                
                return stats
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing CSV file: {str(e)}"))
            return stats
    
    def process_json_file(self, json_path: str) -> Dict[str, int]:
        """Process a JSON file containing knowledge base entries."""
        stats = {'created': 0, 'skipped': 0, 'errors': 0}
        
        # Check if file exists
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"JSON file does not exist: {json_path}"))
            return stats
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check if data is a list
                if not isinstance(data, list):
                    self.stdout.write(self.style.ERROR("JSON file must contain a list of entries"))
                    return stats
                
                # Process entries
                with transaction.atomic():
                    for entry in data:
                        try:
                            # Check required fields
                            if 'title' not in entry or 'content' not in entry:
                                self.stdout.write(self.style.WARNING(
                                    "Skipping entry without title or content"
                                ))
                                stats['skipped'] += 1
                                continue
                            
                            # Get course and module if specified
                            course = None
                            module = None
                            
                            if 'course_id' in entry and entry['course_id']:
                                try:
                                    course = Course.objects.get(id=int(entry['course_id']))
                                except (Course.DoesNotExist, ValueError):
                                    self.stdout.write(self.style.WARNING(
                                        f"Course with ID {entry['course_id']} not found"
                                    ))
                            
                            if 'module_id' in entry and entry['module_id']:
                                try:
                                    module = Module.objects.get(id=int(entry['module_id']))
                                except (Module.DoesNotExist, ValueError):
                                    self.stdout.write(self.style.WARNING(
                                        f"Module with ID {entry['module_id']} not found"
                                    ))
                            
                            # Check if entry already exists
                            existing = TutorKnowledgeBase.objects.filter(
                                title=entry['title'],
                                course=course,
                                module=module
                            ).first()
                            
                            if existing:
                                self.stdout.write(f"Skipping existing entry: {entry['title']}")
                                stats['skipped'] += 1
                                continue
                            
                            # Create new entry
                            TutorKnowledgeBase.objects.create(
                                title=entry['title'],
                                content=entry['content'],
                                course=course,
                                module=module
                            )
                            
                            stats['created'] += 1
                            self.stdout.write(f"Created entry: {entry['title']}")
                            
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error processing entry: {str(e)}"))
                            stats['errors'] += 1
                
                return stats
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing JSON file: {str(e)}"))
            return stats
    
    def process_modules(self) -> Dict[str, int]:
        """Create knowledge base entries from existing course modules."""
        stats = {'created': 0, 'skipped': 0, 'errors': 0}
        
        try:
            # Get all modules with content
            modules = Module.objects.filter(content__isnull=False).exclude(content='')
            
            if not modules.exists():
                self.stdout.write(self.style.WARNING("No modules with content found"))
                return stats
            
            # Process modules
            with transaction.atomic():
                for module in modules:
                    try:
                        # Skip if already exists
                        existing = TutorKnowledgeBase.objects.filter(
                            module=module,
                            course=module.course
                        ).first()
                        
                        if existing:
                            self.stdout.write(f"Skipping existing module: {module.title}")
                            stats['skipped'] += 1
                            continue
                        
                        # Create knowledge base entry
                        TutorKnowledgeBase.objects.create(
                            title=module.title,
                            content=module.content,
                            course=module.course,
                            module=module
                        )
                        
                        stats['created'] += 1
                        self.stdout.write(f"Created entry from module: {module.title}")
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f"Error processing module {module.id} - {module.title}: {str(e)}"
                        ))
                        stats['errors'] += 1
            
            return stats
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing modules: {str(e)}"))
            return stats