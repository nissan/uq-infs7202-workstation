from django.contrib import admin
from .models import QRCode, QRCodeScan

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'url', 'created_at', 'last_used', 'scan_count')
    list_filter = ('content_type', 'created_at', 'last_used')
    search_fields = ('url',)
    readonly_fields = ('code', 'created_at', 'last_used', 'scan_count')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content_type')

@admin.register(QRCodeScan)
class QRCodeScanAdmin(admin.ModelAdmin):
    list_display = ('qr_code', 'scanned_at', 'ip_address')
    list_filter = ('scanned_at', 'ip_address')
    search_fields = ('qr_code__url', 'ip_address')
    readonly_fields = ('scanned_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('qr_code')
