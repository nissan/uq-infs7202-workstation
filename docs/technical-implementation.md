# Technical Implementation Plan

## Overview
This document outlines the technical implementation plan for the Enhanced LearnMore platform, including recommended Django features, extensions, and implementation strategies.

## Django Features to Leverage

### Built-in Features
- Django's ContentTypes framework for polymorphic relationships
- Django's built-in permission system
- Django's session framework
- Django's form validation
- Django's caching framework
- Django's signals for event handling

### Recommended Extensions
- `django-allauth` for social authentication
- `django-rest-framework` for API endpoints
- `django-filter` for advanced filtering
- `django-cors-headers` for API access
- `django-storages` for file storage
- `django-celery-beat` for scheduled tasks

## Implementation Priorities

### 1. QR Code Generation
- Implement QR code generation for courses, modules, and content
- Add QR code management interface
- Implement QR code analytics
- Add printable QR code sheets

### 2. AI Tutor Integration
- Implement LangChain integration using updated provider-specific packages
  - langchain-huggingface for embeddings
  - langchain-ollama for local LLM access
  - langchain-chroma for vector storage
- Support both Ollama (local) and OpenAI (production)
- Add conversation history
- Implement RAG for course content with Chroma vector DB
- Add analytics for AI interactions

### 3. Multi-tenant Features
- Implement institution model
- Add institution membership
- Implement SSO integration
- Add institution-specific branding

### 4. Subscription Management
- Implement subscription plans
- Add subscription tracking
- Implement billing integration
- Add usage analytics

## Required Dependencies
```
django-allauth
djangorestframework
django-filter
django-cors-headers
django-storages
django-celery-beat
langchain-core
langchain-community
langchain-openai
langchain-ollama
langchain-huggingface
langchain-chroma
chromadb
qrcode
pillow
```

## Model Structures

### QR Code Model
```python
class QRCode(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    code = models.ImageField(upload_to='qr_codes/')
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    scan_count = models.IntegerField(default=0)
```

### LLM Interaction Model
```python
class LLMInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    model_used = models.CharField(max_length=50)  # 'ollama' or 'openai'
    tokens_used = models.IntegerField(default=0)
```

### Institution Model
```python
class Institution(models.Model):
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200, unique=True)
    logo = models.ImageField(upload_to='institution_logos/')
    created_at = models.DateTimeField(auto_now_add=True)
```

### Subscription Models
```python
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()
    max_users = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Subscription(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20)
```

## Settings Configuration
```python
INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'storages',
    'django_celery_beat',
]

# LangChain settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
DEFAULT_LLM_MODEL = os.getenv('DEFAULT_LLM_MODEL', 'llama3')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME', 'llama3')
OLLAMA_EMBEDDING_MODEL = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
VECTOR_DB_PATH = os.path.join(BASE_DIR, 'vectorstore')
```

## Implementation Notes
- Use Django's ContentTypes framework for polymorphic relationships
- Implement proper indexing for performance
- Use Django's built-in caching for frequently accessed data
- Implement proper error handling and logging
- Follow Django's best practices for security
- Use Django's form validation for all user inputs
- Implement proper testing for all new features 