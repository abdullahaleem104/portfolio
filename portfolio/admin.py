from django.contrib import admin
from .models import Technology, Project, ProjectImage, Feature, ContactMessage

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_active']
    list_filter = ['is_active', 'technologies']
    search_fields = ['title', 'description']
    filter_horizontal = ['technologies']
    inlines = [ProjectImageInline, FeatureInline]
    prepopulated_fields = {}  # Remove if you have slug field

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'ip_address', 'created_at']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"