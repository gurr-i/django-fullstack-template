from django.contrib import admin
from .models import (
    UserProfile, TaskCategory, Task, TaskComment, 
    TaskAttachment, Notification
)

class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0

class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_joined', 'website')
    search_fields = ('user__username', 'user__email', 'bio')
    list_filter = ('date_joined',)

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name', 'description')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'assigned_to', 'due_date', 'status', 'priority')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('title', 'description', 'created_by__username', 'assigned_to__username')
    date_hierarchy = 'created_at'
    inlines = [TaskCommentInline, TaskAttachmentInline]
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Assignment Details', {
            'fields': ('created_by', 'assigned_to', 'category')
        }),
        ('Status Information', {
            'fields': ('status', 'priority', 'due_date')
        }),
    )

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'task__title', 'user__username')

@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'uploaded_by', 'uploaded_at', 'description')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('description', 'task__title', 'uploaded_by__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('message', 'user__username')
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"

# Customize admin site
admin.site.site_header = "Task Manager Admin"
admin.site.site_title = "Task Manager Admin Portal"
admin.site.index_title = "Welcome to Task Manager Admin Portal"
