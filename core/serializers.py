from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Task, TaskCategory, TaskComment, 
    UserProfile, TaskAttachment, Notification
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'profile_picture', 'date_joined', 'website']


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = ['id', 'name', 'description', 'color']


class TaskCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'content', 'created_at']
        read_only_fields = ['task', 'user']


class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = ['id', 'task', 'file', 'uploaded_by', 'uploaded_at', 'description']
        read_only_fields = ['task', 'uploaded_by']


class TaskSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=TaskCategory.objects.all(),
        required=False,
        allow_null=True
    )
    comments_count = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'created_at', 'updated_at',
            'due_date', 'priority', 'status', 'created_by', 'assigned_to',
            'category', 'comments_count', 'is_overdue'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return obj.comments.count()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'notification_type', 'task', 'message', 'created_at', 'is_read']
        read_only_fields = ['user', 'notification_type', 'task', 'message', 'created_at']
