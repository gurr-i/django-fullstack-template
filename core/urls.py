from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet, basename='api-task')
router.register(r'categories', views.TaskCategoryViewSet, basename='api-category')
router.register(r'profiles', views.UserProfileViewSet, basename='api-profile')
router.register(r'notifications', views.NotificationViewSet, basename='api-notification')

urlpatterns = [
    # Web views
    path('', views.HomeView.as_view(), name='home'),
    path('tasks/', views.TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task-delete'),
    
    # User profiles
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='user-profile'),
    
    # Authentication
    path('register/', views.register, name='register'),
    
    # Notifications
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    
    # API endpoints
    path('api/', include(router.urls)),
]
