# QR Code System Demo Guide

This guide outlines how to use and demonstrate the QR code system in the LearnMore platform.

## Setting Up the Demo

The QR code demo data is automatically created when you run the platform setup:

```bash
# Run the full setup script
./setup_demo_env.sh

# Or run just the QR code demo data script
python create_qr_demo_data.py
```

## Demo Features

The QR code system provides the following features:

1. **QR Codes for Various Content Types**:
   - Course QR codes for quick course access
   - Module QR codes with different access levels
   - Quiz QR codes with tracking capabilities

2. **Access Control Levels**:
   - Public: Anyone can scan
   - Enrolled: Only enrolled students can access
   - Instructor: Only instructors can access

3. **QR Code Management**:
   - Individual QR code generation
   - Batch operations for creating multiple codes
   - Statistics and analytics

4. **Tracking Integration**:
   - QR scans are tracked in user progress
   - Scan history with timestamps and locations
   - Analytics for QR code usage

## Demo Accounts

Use these accounts to demonstrate different access levels:

- **Admin**: 
  - Username: admin
  - Password: admin123
  - Full access to all QR code features

- **Instructor**: 
  - Username: instructor
  - Password: instructor123
  - Can create and manage QR codes

- **Student**: 
  - Username: student
  - Password: student123
  - Can scan QR codes based on access level

## Demo Walkthrough

### 1. QR Code Management (Admin/Instructor)

1. Log in as admin or instructor
2. Go to Admin → QR Codes
3. Browse existing QR codes and batches
4. Create a new QR code:
   - Select content type (course, module, quiz)
   - Choose access level
   - Configure optional settings (expiration, scan limits)
   - Generate and download

### 2. QR Code Scanning (Student)

1. Log in as a student
2. Go to the QR Code Scanner (/qr-codes/scanner/)
3. Allow camera access
4. Scan a QR code
5. View the scan result and navigate to content

### 3. Analytics (Admin/Instructor)

1. Log in as admin or instructor
2. Go to QR Code Analytics (/qr-codes/analytics/)
3. View scan statistics, charts, and reports
4. Explore individual QR code performance

## API Examples

The QR code system offers a comprehensive API:

```
# List all QR codes
GET /api/qr-codes/

# Get a specific QR code
GET /api/qr-codes/{id}/

# Create a new QR code
POST /api/qr-codes/

# Process a scan
POST /api/qr-codes/scans/scan/

# Create a batch
POST /api/qr-codes/batches/
```

## Integration Points

The QR code system integrates with:

1. **Course System**:
   - Course model has `qr_enabled` flag
   - Quick access to course content

2. **Module System**:
   - Module model has `qr_access` field
   - Different access levels for different modules

3. **Quiz System**:
   - Quiz model has `qr_tracking` flag
   - QR codes can be used for quiz access

4. **Progress Tracking**:
   - Progress model has `qr_scans` JSON field
   - Scans are tracked as part of learning progress