from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Task, UserProfile, Notification


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for each new User"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    """Create notifications for task events"""
    if created:
        # New task assigned notification
        if instance.assigned_to and instance.assigned_to != instance.created_by:
            Notification.objects.create(
                user=instance.assigned_to,
                notification_type='task_assigned',
                task=instance,
                message=f"{instance.created_by.username} assigned you the task '{instance.title}'"
            )
    else:
        # Get the previous state of the task before changes
        try:
            old_task = Task.objects.get(id=instance.id)
            
            # If status changed
            if old_task.status != instance.status:
                # Notify task creator if they're not the one who made the change
                if instance.created_by != instance.assigned_to and instance.assigned_to:
                    Notification.objects.create(
                        user=instance.created_by,
                        notification_type='task_updated',
                        task=instance,
                        message=f"{instance.assigned_to.username} updated the status of '{instance.title}' to {instance.status.replace('_', ' ').title()}"
                    )
            
            # If assigned user changed
            if old_task.assigned_to != instance.assigned_to and instance.assigned_to:
                Notification.objects.create(
                    user=instance.assigned_to,
                    notification_type='task_assigned',
                    task=instance,
                    message=f"{instance.created_by.username} assigned you the task '{instance.title}'"
                )
                
        except Task.DoesNotExist:
            # Task was just created, already handled above
            pass


@receiver(pre_save, sender=Task)
def check_due_date_approaching(sender, instance, **kwargs):
    """Check if task due date is approaching and create notification"""
    if instance.due_date and not instance.is_overdue:
        # Check if the task is due within the next 24 hours
        time_until_due = instance.due_date - timezone.now()
        
        # If due in less than 24 hours but more than 23 hours (to avoid multiple notifications)
        if time_until_due.total_seconds() < 86400 and time_until_due.total_seconds() > 82800:
            # Notify assigned user
            if instance.assigned_to:
                Notification.objects.create(
                    user=instance.assigned_to,
                    notification_type='due_soon',
                    task=instance,
                    message=f"Task '{instance.title}' is due in less than 24 hours"
                )
            
            # Notify task creator as well if they're not the assigned user
            if instance.created_by != instance.assigned_to:
                Notification.objects.create(
                    user=instance.created_by,
                    notification_type='due_soon',
                    task=instance,
                    message=f"Task '{instance.title}' is due in less than 24 hours"
                )
