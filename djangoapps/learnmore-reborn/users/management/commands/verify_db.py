from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import sys

class Command(BaseCommand):
    help = 'Verifies the database connection and prints connection details'

    def handle(self, *args, **options):
        try:
            # Get the default database connection
            conn = connections['default']
            conn.ensure_connection()
            
            # Get database info
            db_info = conn.get_connection_params()
            
            # Print connection info (excluding sensitive data)
            self.stdout.write(self.style.SUCCESS('Database connection successful!'))
            self.stdout.write(f"Database engine: {db_info.get('ENGINE', 'Unknown')}")
            self.stdout.write(f"Database name: {db_info.get('NAME', 'Unknown')}")
            self.stdout.write(f"Database host: {db_info.get('HOST', 'Unknown')}")
            self.stdout.write(f"Database port: {db_info.get('PORT', 'Unknown')}")
            self.stdout.write(f"Database user: {db_info.get('USER', 'Unknown')}")
            
            # Test a simple query
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                self.stdout.write(f"Database version: {version[0] if version else 'Unknown'}")
                
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f'Database connection failed: {str(e)}'))
            sys.exit(1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
            sys.exit(1) 