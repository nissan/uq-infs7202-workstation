#!/bin/bash
set -e

echo "Setting up demo environment..."

echo "Removing local database (db.sqlite3) ..."
rm -f db.sqlite3

echo "Running migrations (re-creating tables) ..."
python manage.py migrate

echo "Flushing (clearing out) any stale data (if any) ..."
python manage.py flush --no-input

echo "Creating test users..."
python manage.py shell < create_test_users.py

echo "Creating test content..."
python manage.py shell < create_test_content.py

echo "Creating test quizzes..."
python manage.py shell < create_test_quiz.py

echo "Creating general test data..."
python manage.py shell < create_test_data.py

echo "Creating demo RAG content..."
python manage.py shell < create_demo_rag_content.py

echo "Ingesting RAG content..."
python manage.py shell < ingest_rag_content.py

echo "Creating QR code demo data..."
python create_qr_demo_data.py

echo "Demo environment setup complete!"