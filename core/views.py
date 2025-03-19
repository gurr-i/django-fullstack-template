from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Task, TaskCategory, TaskComment, UserProfile, Notification
from .forms import TaskForm, TaskCommentForm, UserProfileForm, TaskCategoryForm, CustomUserCreationForm
from .serializers import (
    TaskSerializer, TaskCategorySerializer, TaskCommentSerializer, 
    UserProfileSerializer, NotificationSerializer
)

# Error handlers
def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

class HomeView(TemplateView):
    template_name = 'core/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['recent_tasks'] = Task.objects.filter(
                Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
            ).order_by('-created_at')[:5]
            
            # Get counts for dashboard
            context['pending_count'] = Task.objects.filter(
                (Q(created_by=self.request.user) | Q(assigned_to=self.request.user)),
                status='pending'
            ).count()
            
            context['in_progress_count'] = Task.objects.filter(
                (Q(created_by=self.request.user) | Q(assigned_to=self.request.user)),
                status='in_progress'
            ).count()
            
            context['completed_count'] = Task.objects.filter(
                (Q(created_by=self.request.user) | Q(assigned_to=self.request.user)),
                status='completed'
            ).count()
            
            # Get overdue tasks
            context['overdue_tasks'] = Task.objects.filter(
                (Q(created_by=self.request.user) | Q(assigned_to=self.request.user)),
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).order_by('due_date')[:5]
            
            # Get notifications
            context['notifications'] = Notification.objects.filter(
                user=self.request.user,
                is_read=False
            )[:5]
        
        return context


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'core/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Task.objects.filter(
            Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
        )
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by priority if provided
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        # Filter by category if provided
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__id=category)
            
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = TaskCategory.objects.all()
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'core/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = TaskCommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = TaskCommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = self.object
            comment.user = request.user
            comment.save()
            
            # Create notification for task owner
            if self.object.created_by != request.user:
                Notification.objects.create(
                    user=self.object.created_by,
                    notification_type='comment_added',
                    task=self.object,
                    message=f"{request.user.username} commented on your task '{self.object.title}'"
                )
            
            # Create notification for assigned user
            if self.object.assigned_to and self.object.assigned_to != request.user:
                Notification.objects.create(
                    user=self.object.assigned_to,
                    notification_type='comment_added',
                    task=self.object,
                    message=f"{request.user.username} commented on task '{self.object.title}' assigned to you"
                )
                
            messages.success(request, "Comment added successfully.")
            return redirect('task-detail', pk=self.object.pk)
        
        context = self.get_context_data(object=self.object)
        context['comment_form'] = form
        return self.render_to_response(context)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'core/task_form.html'
    success_url = reverse_lazy('task-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Create notification for assigned user
        if form.instance.assigned_to and form.instance.assigned_to != self.request.user:
            Notification.objects.create(
                user=form.instance.assigned_to,
                notification_type='task_assigned',
                task=form.instance,
                message=f"{self.request.user.username} assigned you the task '{form.instance.title}'"
            )
            
        messages.success(self.request, "Task created successfully.")
        return response


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'core/task_form.html'
    
    def form_valid(self, form):
        old_assigned = self.get_object().assigned_to
        response = super().form_valid(form)
        
        # If assigned user changed, create notification
        if form.instance.assigned_to and form.instance.assigned_to != old_assigned:
            Notification.objects.create(
                user=form.instance.assigned_to,
                notification_type='task_assigned',
                task=form.instance,
                message=f"{self.request.user.username} assigned you the task '{form.instance.title}'"
            )
        
        # Create notification for task updates
        if old_assigned and old_assigned != self.request.user:
            Notification.objects.create(
                user=old_assigned,
                notification_type='task_updated',
                task=form.instance,
                message=f"{self.request.user.username} updated the task '{form.instance.title}'"
            )
            
        messages.success(self.request, "Task updated successfully.")
        return response
    
    def test_func(self):
        task = self.get_object()
        return task.created_by == self.request.user or task.assigned_to == self.request.user
    
    def get_success_url(self):
        return reverse_lazy('task-detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'core/task_confirm_delete.html'
    success_url = reverse_lazy('task-list')
    
    def test_func(self):
        task = self.get_object()
        return task.created_by == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Task deleted successfully.")
        return super().delete(request, *args, **kwargs)


@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
        
    # Get or create user profile
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST' and user == request.user:
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Get user's tasks
    created_tasks = Task.objects.filter(created_by=user).order_by('-created_at')[:5]
    assigned_tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'profile_user': user,
        'form': form,
        'created_tasks': created_tasks,
        'assigned_tasks': assigned_tasks,
        'is_own_profile': user == request.user
    }
    
    return render(request, 'core/profile.html', context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.task:
        return redirect('task-detail', pk=notification.task.pk)
    
    return redirect('home')


# API ViewSets
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(
            Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        task = self.get_object()
        serializer = TaskCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        task = self.get_object()
        comments = task.comments.all()
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)


class TaskCategoryViewSet(viewsets.ModelViewSet):
    queryset = TaskCategory.objects.all()
    serializer_class = TaskCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})
