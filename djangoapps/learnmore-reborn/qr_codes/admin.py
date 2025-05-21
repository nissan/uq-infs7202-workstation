from django.contrib import admin
from django.utils.html import format_html
from .models import QRCode, QRCodeScan, QRCodeBatch

class QRCodeScanInline(admin.TabularInline):
    model = QRCodeScan
    extra = 0
    readonly_fields = ['id', 'scanned_at', 'user', 'ip_address', 'status']
    can_delete = False
    max_num = 10
    fields = ['scanned_at', 'user', 'ip_address', 'status']
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'target_display', 'created_at', 'scan_count_display', 'is_active_display', 'expires_at']
    list_filter = ['is_active', 'access_level', 'content_type', 'batch']
    search_fields = ['id', 'payload']
    readonly_fields = ['id', 'created_at', 'current_scans', 'qr_code_preview']
    inlines = [QRCodeScanInline]
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'created_at', 'expires_at')
        }),
        ('Target', {
            'fields': ('content_type', 'object_id')
        }),
        ('Configuration', {
            'fields': ('is_active', 'access_level', 'max_scans', 'current_scans')
        }),
        ('Batch', {
            'fields': ('batch',)
        }),
        ('QR Code Data', {
            'fields': ('payload', 'qr_code_preview')
        }),
    )
    
    def target_display(self, obj):
        """Display the target object information."""
        return f"{obj.content_type.model}: {obj.object_id}"
    target_display.short_description = "Target"
    
    def scan_count_display(self, obj):
        """Display the scan count with progress bar if max_scans is set."""
        if obj.max_scans:
            percentage = min(100, int((obj.current_scans / obj.max_scans) * 100))
            return format_html(
                '<div style="width:100%%; background-color:#f8f8f8; border-radius:3px;">'
                '<div style="width:%d%%; background-color:%s; height:10px; border-radius:3px;"></div>'
                '</div><span>%d/%d (%d%%)</span>' % 
                (percentage, '#4CAF50' if percentage < 80 else '#FFC107' if percentage < 100 else '#F44336',
                 obj.current_scans, obj.max_scans, percentage)
            )
        return obj.current_scans
    scan_count_display.short_description = "Scans"
    
    def is_active_display(self, obj):
        """Display the active status with a colored indicator."""
        return format_html(
            '<span style="color:%s;">%s</span>' % 
            ('#4CAF50' if obj.is_active else '#F44336', 
             'Active' if obj.is_active else 'Inactive')
        )
    is_active_display.short_description = "Status"
    
    def qr_code_preview(self, obj):
        """Display the QR code image if available."""
        if obj.image_data:
            return format_html('<img src="data:image/png;base64,{}" style="max-width:200px; max-height:200px;" />', obj.image_data)
        return "No QR code image available"
    qr_code_preview.short_description = "QR Code Preview"


@admin.register(QRCodeScan)
class QRCodeScanAdmin(admin.ModelAdmin):
    list_display = ['id', 'qr_code', 'user', 'scanned_at', 'status', 'ip_address']
    list_filter = ['status', 'scanned_at']
    search_fields = ['id', 'qr_code__id', 'user__username', 'ip_address']
    readonly_fields = ['id', 'qr_code', 'scanned_at', 'user', 'ip_address', 'user_agent', 
                      'latitude', 'longitude', 'context_data']
    fieldsets = (
        ('Scan Information', {
            'fields': ('id', 'qr_code', 'scanned_at', 'status')
        }),
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Location Data', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('context_data',)
        }),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(QRCodeBatch)
class QRCodeBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'created_by', 'codes_count', 'scans_count', 'is_active']
    list_filter = ['is_active', 'created_at', 'access_level']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['id', 'created_at', 'codes_count', 'scans_count']
    fieldsets = (
        ('Batch Information', {
            'fields': ('id', 'name', 'description', 'created_at', 'created_by')
        }),
        ('Target', {
            'fields': ('content_type', 'target_type')
        }),
        ('Configuration', {
            'fields': ('is_active', 'access_level', 'max_scans_per_code', 'expires_at')
        }),
        ('Statistics', {
            'fields': ('codes_count', 'scans_count')
        }),
        ('Additional Data', {
            'fields': ('metadata',)
        }),
    )