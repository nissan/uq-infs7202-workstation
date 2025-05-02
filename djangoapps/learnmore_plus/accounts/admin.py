from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.contenttypes.models import ContentType
from .models import UserProfile, ModuleNotes

class CustomUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        # Check if user has admin group or is superuser
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Administrator', 'Course Coordinator']).exists()

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

class CustomGroupAdmin(GroupAdmin):
    """Custom admin interface for managing groups and permissions."""
    list_display = ('name', 'get_permission_count', 'get_user_count')
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)

    def get_permission_count(self, obj):
        return obj.permissions.count()
    get_permission_count.short_description = 'Permissions'

    def get_user_count(self, obj):
        return obj.user_set.count()
    get_user_count.short_description = 'Users'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('permissions', 'user_set')

class PermissionAdmin(admin.ModelAdmin):
    """Admin interface for managing permissions."""
    list_display = ('name', 'codename', 'content_type')
    list_filter = ('content_type',)
    search_fields = ('name', 'codename')
    ordering = ('content_type__app_label', 'content_type__model', 'codename')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_groups', 'get_primary_group', 'date_joined', 'last_login')
    list_filter = ('user__groups', 'date_joined', 'last_login')
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'location', 'birth_date', 'avatar')
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.user.groups.all()])
    get_groups.short_description = 'Groups'

    def get_primary_group(self, obj):
        return obj.get_primary_group()
    get_primary_group.short_description = 'Primary Group'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related('user__groups')

@admin.register(ModuleNotes)
class ModuleNotesAdmin(admin.ModelAdmin):
    list_display = ('user', 'module_id', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'module_id', 'notes')
    raw_id_fields = ('user',)

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Administrator', 'Course Coordinator']).exists()

# Register models
admin.site.unregister(User)  # Unregister default User admin
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)  # Unregister default Group admin
admin.site.register(Group, CustomGroupAdmin)

admin.site.register(Permission, PermissionAdmin)
