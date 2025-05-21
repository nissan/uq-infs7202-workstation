# QR Code Module

This module provides QR code generation, scanning, and management capabilities for the LearnMore platform.

## Features

- **QR Code Generation**: Create QR codes for courses, modules, quizzes, and other content
- **QR Code Scanning**: Mobile-friendly QR code scanner
- **Batch Operations**: Create and manage batches of QR codes
- **Analytics**: Track usage and view statistics for QR codes
- **Access Control**: Control who can scan QR codes with access levels
- **Time & Usage Limits**: Set expiration dates and usage limits for QR codes

## Models

### QRCode

The primary model for storing QR code information:

- **UUID-based ID**: For secure identification
- **Content Type & Object ID**: Generic foreign key to associate with any model
- **Configuration**: Access levels, scan limits, expiration dates
- **Media**: Base64-encoded QR code image
- **Tracking**: Scan counts and statistics

### QRCodeScan

Tracks each scan of a QR code:

- **Scanner Information**: User, IP address, user agent
- **Location Data**: Optional geographical data
- **Context Data**: Additional information about the scan
- **Timestamps**: When the scan occurred

### QRCodeBatch

Manages groups of related QR codes:

- **Batch Properties**: Name, description, target type
- **Batch Configuration**: Access levels, scan limits, etc.
- **Statistics**: Aggregate data about codes and scans

## API Endpoints

### QR Code Management

- `GET /api/qr-codes/`: List all QR codes
- `POST /api/qr-codes/`: Create a new QR code
- `GET /api/qr-codes/{id}/`: Get a specific QR code
- `PUT /api/qr-codes/{id}/`: Update a QR code
- `DELETE /api/qr-codes/{id}/`: Delete a QR code
- `GET /api/qr-codes/{id}/regenerate/`: Regenerate QR code image
- `GET /api/qr-codes/{id}/scans/`: Get scan history for a QR code

### QR Code Scanning

- `POST /api/qr-codes/scans/scan/`: Process a QR code scan

### Batch Operations

- `GET /api/qr-codes/batches/`: List all batches
- `POST /api/qr-codes/batches/`: Create a new batch
- `GET /api/qr-codes/batches/{id}/`: Get a specific batch
- `PUT /api/qr-codes/batches/{id}/`: Update a batch
- `DELETE /api/qr-codes/batches/{id}/`: Delete a batch
- `POST /api/qr-codes/batches/{id}/generate-codes/`: Generate QR codes for a batch
- `GET /api/qr-codes/batches/{id}/codes/`: Get all QR codes in a batch
- `GET /api/qr-codes/batches/{id}/stats/`: Get statistics for a batch

## User Interfaces

### Generator

- Create individual QR codes
- Configure access levels and limits
- Download as image
- Create batches

### Scanner

- Mobile-friendly QR code scanner
- Camera access with device selection
- Scan history and tracking
- Redirect to scanned content

### Management

- View and search QR codes
- Download and print QR codes
- Manage batches
- View scan history

### Analytics

- View usage statistics
- Download reports
- Analyze scan patterns
- Track effectiveness

## Implementation Details

### QR Code Generation

The QR code generation uses the `qrcode` Python library to create standard QR codes with the following format:

```json
{
  "id": "uuid-goes-here",
  "type": "app_label.model_name",
  "target_id": 123
}
```

Additional payload data can be included as needed.

### Scanning Process

1. User scans QR code with camera
2. QR code data is sent to server
3. Server validates QR code and checks access permissions
4. Server records scan in database
5. Server returns target information and URL
6. User is redirected to the appropriate content

### Dependencies

- `qrcode`: For generating QR codes
- `Pillow`: For image processing
- `pyzbar` (optional): For server-side QR code detection

## Installation

1. Add `qr_codes` to `INSTALLED_APPS` in settings.py
2. Run migrations: `python manage.py migrate qr_codes`
3. Install dependencies: `pip install qrcode Pillow`
4. Include URLs in your project's URLconf:

```python
path('qr-codes/', include('qr_codes.urls')),
path('api/qr-codes/', include('qr_codes.api_urls')),
```

## Usage Examples

### Creating a QR Code Programmatically

```python
from django.contrib.contenttypes.models import ContentType
from courses.models import Course
from qr_codes.models import QRCode
from qr_codes.services import QRCodeService

# Get content type for a Course
course = Course.objects.get(id=1)
content_type = ContentType.objects.get_for_model(Course)

# Create QR code
qr_code = QRCode.objects.create(
    content_type=content_type,
    object_id=course.id,
    is_active=True,
    access_level='public'
)

# Generate QR code image
QRCodeService.generate_qr_image(qr_code)

# Get image data
image_data = qr_code.image_data  # Base64 encoded image
```

### Processing a Scan

```python
from qr_codes.services import QRCodeService

# Validate a scan
is_valid, message, qr_code = QRCodeService.validate_scan(
    qr_code_id='uuid-goes-here',
    user=request.user
)

if is_valid:
    # Record the scan
    scan = QRCodeScan.objects.create(
        qr_code=qr_code,
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR'),
        status='success'
    )
    
    # Update scan count
    qr_code.current_scans += 1
    qr_code.save()
```

## Future Enhancements

1. **Custom QR Styling**: Add support for branded QR codes with logos and colors
2. **Offline Scanning**: Enable scanning without internet connection
3. **Analytics Improvements**: Add heatmaps, conversion tracking, etc.
4. **Integration with LMS**: Connect QR codes to course completion and progress
5. **Mobile App Support**: Integration with native mobile apps