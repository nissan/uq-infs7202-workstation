from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import QRCode, QRCodeScan, QRCodeBatch


class ContentTypeField(serializers.Field):
    """Custom field for handling ContentType objects."""
    
    def to_representation(self, obj):
        return {
            'app_label': obj.app_label,
            'model': obj.model,
            'id': obj.id
        }
    
    def to_internal_value(self, data):
        if isinstance(data, dict) and 'app_label' in data and 'model' in data:
            try:
                return ContentType.objects.get(app_label=data['app_label'], model=data['model'])
            except ContentType.DoesNotExist:
                raise serializers.ValidationError(f"ContentType with app_label={data['app_label']} and model={data['model']} does not exist")
        elif isinstance(data, int):
            try:
                return ContentType.objects.get(id=data)
            except ContentType.DoesNotExist:
                raise serializers.ValidationError(f"ContentType with id={data} does not exist")
        else:
            raise serializers.ValidationError("Invalid content_type format. Must be either an id or an object with app_label and model")


class QRCodeSerializer(serializers.ModelSerializer):
    """Serializer for retrieving QR code data."""
    id = serializers.UUIDField(read_only=True)  # Explicitly define id field
    content_type = ContentTypeField()
    scan_count = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_scan_limit_reached = serializers.ReadOnlyField()
    is_scannable = serializers.ReadOnlyField()
    
    class Meta:
        model = QRCode
        fields = [
            'id', 'created_at', 'expires_at', 'content_type', 'object_id',
            'max_scans', 'current_scans', 'is_active', 'access_level',
            'payload', 'image_data', 'batch', 'scan_count', 'is_expired',
            'is_scan_limit_reached', 'is_scannable'
        ]
        read_only_fields = ['id', 'created_at', 'current_scans', 'scan_count', 
                            'is_expired', 'is_scan_limit_reached', 'is_scannable']


class QRCodeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating QR codes."""
    content_type = ContentTypeField()
    
    class Meta:
        model = QRCode
        fields = [
            'content_type', 'object_id', 'expires_at', 'max_scans',
            'is_active', 'access_level', 'payload', 'batch'
        ]
    
    def validate(self, data):
        """Validate that the content object exists."""
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        
        if content_type and object_id:
            try:
                content_type.get_object_for_this_type(pk=object_id)
            except Exception:
                raise serializers.ValidationError(
                    f"Object with id={object_id} does not exist in {content_type.app_label}.{content_type.model}"
                )
        
        return data


class QRCodeScanSerializer(serializers.ModelSerializer):
    """Serializer for QR code scans."""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = QRCodeScan
        fields = [
            'id', 'qr_code', 'scanned_at', 'user', 'ip_address',
            'user_agent', 'latitude', 'longitude', 'context_data', 'status'
        ]
        read_only_fields = ['id', 'scanned_at', 'user', 'status']


class QRCodeScanRequestSerializer(serializers.Serializer):
    """Serializer for handling QR code scan requests."""
    qr_code_id = serializers.UUIDField()
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)
    context_data = serializers.JSONField(required=False, default=dict)


class QRCodeScanResponseSerializer(serializers.Serializer):
    """Serializer for QR code scan responses."""
    success = serializers.BooleanField()
    status = serializers.CharField()
    message = serializers.CharField()
    target_type = serializers.CharField()
    target_id = serializers.IntegerField()
    target_url = serializers.CharField(required=False, allow_null=True)
    additional_data = serializers.JSONField(required=False)
    scan_id = serializers.UUIDField(required=False, allow_null=True)


class QRCodeBatchSerializer(serializers.ModelSerializer):
    """Serializer for QR code batches."""
    content_type = ContentTypeField(required=False, allow_null=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    codes_count = serializers.ReadOnlyField()
    scans_count = serializers.ReadOnlyField()
    
    class Meta:
        model = QRCodeBatch
        fields = [
            'id', 'name', 'description', 'created_at', 'created_by',
            'content_type', 'target_type', 'expires_at', 'access_level',
            'max_scans_per_code', 'is_active', 'codes_count', 'scans_count', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'codes_count', 'scans_count']


class QRCodeBatchCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating batches of QR codes."""
    content_type = ContentTypeField(required=False, allow_null=True)
    target_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of target object IDs to create QR codes for"
    )
    
    class Meta:
        model = QRCodeBatch
        fields = [
            'name', 'description', 'content_type', 'target_type',
            'expires_at', 'access_level', 'max_scans_per_code',
            'is_active', 'metadata', 'target_ids'
        ]
    
    def validate(self, data):
        """Validate that the content type is provided if target_ids are specified."""
        target_ids = data.get('target_ids', [])
        content_type = data.get('content_type')
        
        if target_ids and not content_type:
            raise serializers.ValidationError({"content_type": ["Content type is required when target IDs are provided."]})
        
        # Check if each target ID exists for the given content type
        if target_ids and content_type:
            non_existent_ids = []
            for target_id in target_ids:
                try:
                    content_type.get_object_for_this_type(pk=target_id)
                except Exception:
                    non_existent_ids.append(target_id)
            
            if non_existent_ids:
                raise serializers.ValidationError({
                    "target_ids": [f"Objects with IDs {', '.join(map(str, non_existent_ids))} do not exist for the specified content type."]
                })
        
        return data
        
    def create(self, validated_data):
        """Create a QRCodeBatch instance and handle target_ids separately."""
        # Extract target_ids before creating the batch (not a model field)
        target_ids = validated_data.pop('target_ids', [])
        
        # Create the batch
        batch = QRCodeBatch.objects.create(**validated_data)
        
        # Create QR codes if target_ids were provided
        if target_ids and batch.content_type:
            from .services import QRCodeService
            QRCodeService.create_batch_codes(
                batch=batch,
                target_ids=target_ids,
                content_type=batch.content_type,
                expires_at=batch.expires_at,
                max_scans=batch.max_scans_per_code,
                access_level=batch.access_level
            )
            
        return batch