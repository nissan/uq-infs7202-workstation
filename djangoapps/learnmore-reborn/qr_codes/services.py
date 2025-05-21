import qrcode
import base64
import io
import json
import uuid
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

class QRCodeService:
    """Service class for QR code operations."""
    
    @staticmethod
    def generate_qr_image(qr_code_instance):
        """Generate a QR code image and update the instance."""
        # Create data payload
        data = {
            'id': str(qr_code_instance.id),
            'type': f"{qr_code_instance.content_type.app_label}.{qr_code_instance.content_type.model}",
            'target_id': qr_code_instance.object_id
        }
        
        # Include any additional payload data
        if qr_code_instance.payload:
            data.update(qr_code_instance.payload)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(data))
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Update QR code instance
        qr_code_instance.image_data = image_data
        qr_code_instance.save(update_fields=['image_data'])
        
        return image_data
    
    @staticmethod
    @transaction.atomic
    def create_batch_codes(batch, target_ids, content_type, **defaults):
        """Create QR codes for multiple targets in a batch."""
        from .models import QRCode
        
        created_codes = []
        
        for target_id in target_ids:
            # Check if object exists
            try:
                content_type.get_object_for_this_type(pk=target_id)
            except Exception:
                # Skip this target if it doesn't exist
                continue
            
            # Create QR code
            qr_code = QRCode.objects.create(
                content_type=content_type,
                object_id=target_id,
                batch=batch,
                **defaults
            )
            
            # Generate QR code image
            QRCodeService.generate_qr_image(qr_code)
            
            created_codes.append(qr_code)
        
        # Update batch
        batch.codes_count = batch.codes.count()
        batch.save(update_fields=['codes_count'])
        
        return created_codes
    
    @staticmethod
    def validate_scan(qr_code_id, user=None):
        """Validate if a QR code can be scanned."""
        from .models import QRCode
        
        try:
            qr_code = QRCode.objects.get(id=qr_code_id)
        except QRCode.DoesNotExist:
            return False, "QR code not found", None
        
        # Check if QR code is active
        if not qr_code.is_active:
            return False, "QR code is inactive", qr_code
        
        # Check if QR code has expired
        if qr_code.is_expired:
            return False, "QR code has expired", qr_code
        
        # Check if scan limit reached
        if qr_code.is_scan_limit_reached:
            return False, "Scan limit reached", qr_code
        
        # Check access level
        if qr_code.access_level != 'public':
            if not user or not user.is_authenticated:
                return False, "Authentication required", qr_code
            
            if qr_code.access_level == 'instructor' and not hasattr(user, 'is_instructor'):
                return False, "Instructor access required", qr_code
            
            if qr_code.access_level == 'admin' and not user.is_staff:
                return False, "Admin access required", qr_code
            
            if qr_code.access_level == 'enrolled':
                # Check if the QR code is for a course and if user is enrolled
                if qr_code.content_type.model == 'course':
                    from courses.models import Enrollment
                    is_enrolled = Enrollment.objects.filter(
                        course_id=qr_code.object_id,
                        user=user
                    ).exists()
                    
                    if not is_enrolled:
                        return False, "Enrollment required", qr_code
        
        return True, "Valid", qr_code