from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Task, Notification

def create_notification(user, task, notification_type, message):
    """Create a notification for a user"""
    Notification.objects.create(
        user=user,
        task=task,
        notification_type=notification_type,
        message=message
    )

@receiver(post_save, sender=Task)
def task_notification_handler(sender, instance, created, **kwargs):
    """Handle notifications for task creation, updates, and due dates"""
    if created:
        # Notify assigned user about new task
        if instance.assigned_to:
            message = f'You have been assigned a new task: {instance.title}'
            create_notification(
                instance.assigned_to,
                instance,
                'task_assigned',
                message
            )
    else:
        # Notify about status changes
        if instance.tracker.has_changed('status'):
            if instance.assigned_to:
                message = f'Task status updated to {instance.get_status_display()}: {instance.title}'
                create_notification(
                    instance.assigned_to,
                    instance,
                    'status_update',
                    message
                )

def check_due_date_notifications():
    """Check for upcoming and overdue tasks"""
    # Get tasks due in the next 24 hours
    tomorrow = timezone.now() + timezone.timedelta(days=1)
    upcoming_tasks = Task.objects.filter(
        due_date__lte=tomorrow,
        due_date__gt=timezone.now(),
        status__in=['pending', 'in_progress']
    )

    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['pending', 'in_progress']
    )

    # Send notifications for upcoming tasks
    for task in upcoming_tasks:
        if task.assigned_to:
            message = f'Task due soon: {task.title}'
            create_notification(
                task.assigned_to,
                task,
                'due_soon',
                message
            )

    # Send notifications for overdue tasks
    for task in overdue_tasks:
        if task.assigned_to:
            message = f'Task is overdue: {task.title}'
            create_notification(
                task.assigned_to,
                task,
                'overdue',
                message
            )