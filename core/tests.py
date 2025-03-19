from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from .models import Task, TaskCategory, UserProfile, TaskComment


class TaskModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.category = TaskCategory.objects.create(
            name='Test Category',
            description='A test category',
            color='primary'
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            created_by=self.user,
            assigned_to=self.user,
            category=self.category,
            priority='medium',
            status='pending'
        )
    
    def test_task_creation(self):
        """Test that task can be created properly"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.created_by, self.user)
        self.assertEqual(self.task.status, 'pending')
    
    def test_task_str_representation(self):
        """Test the string representation of a task"""
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_task_absolute_url(self):
        """Test the absolute URL of a task"""
        self.assertEqual(self.task.get_absolute_url(), f'/tasks/{self.task.id}/')


class TaskViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.category = TaskCategory.objects.create(
            name='Test Category',
            description='A test category',
            color='primary'
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            created_by=self.user,
            assigned_to=self.user,
            category=self.category,
            priority='medium',
            status='pending'
        )
        
        # Create UserProfile for the test user
        UserProfile.objects.create(user=self.user)
    
    def test_home_view_unauthenticated(self):
        """Test the home view for unauthenticated users"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
    
    def test_home_view_authenticated(self):
        """Test the home view for authenticated users"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')
        # Check context data
        self.assertIn('recent_tasks', response.context)
        self.assertIn('pending_count', response.context)
    
    def test_task_list_view(self):
        """Test the task list view"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_list.html')
        self.assertIn('tasks', response.context)
        self.assertEqual(len(response.context['tasks']), 1)
    
    def test_task_detail_view(self):
        """Test the task detail view"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_detail.html')
        self.assertEqual(response.context['task'], self.task)
    
    def test_task_create_view(self):
        """Test the task create view"""
        self.client.login(username='testuser', password='testpassword')
        
        # Test GET request
        response = self.client.get(reverse('task-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_form.html')
        
        # Test POST request with valid data
        task_count = Task.objects.count()
        response = self.client.post(reverse('task-create'), {
            'title': 'New Task',
            'description': 'This is a new task',
            'priority': 'high',
            'status': 'pending',
            'category': self.category.id
        })
        self.assertEqual(Task.objects.count(), task_count + 1)
        self.assertEqual(Task.objects.last().title, 'New Task')
    
    def test_task_update_view(self):
        """Test the task update view"""
        self.client.login(username='testuser', password='testpassword')
        
        # Test GET request
        response = self.client.get(reverse('task-update', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_form.html')
        
        # Test POST request with valid data
        response = self.client.post(reverse('task-update', args=[self.task.id]), {
            'title': 'Updated Task',
            'description': 'This is an updated task',
            'priority': 'high',
            'status': 'in_progress',
            'category': self.category.id
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.status, 'in_progress')
    
    def test_profile_view(self):
        """Test the profile view"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/profile.html')
        self.assertEqual(response.context['profile_user'], self.user)


class TaskAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.category = TaskCategory.objects.create(
            name='Test Category',
            description='A test category',
            color='primary'
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            created_by=self.user,
            assigned_to=self.user,
            category=self.category,
            priority='medium',
            status='pending'
        )
        
        # Authenticate the API client
        self.client.force_authenticate(user=self.user)
    
    def test_get_tasks(self):
        """Test retrieving tasks through the API"""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Task')
    
    def test_create_task(self):
        """Test creating a task through the API"""
        task_count = Task.objects.count()
        response = self.client.post('/api/tasks/', {
            'title': 'API Task',
            'description': 'This task was created through the API',
            'priority': 'high',
            'status': 'pending',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), task_count + 1)
        self.assertEqual(response.data['title'], 'API Task')
    
    def test_update_task(self):
        """Test updating a task through the API"""
        response = self.client.patch(f'/api/tasks/{self.task.id}/', {
            'title': 'Updated API Task',
            'status': 'completed'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated API Task')
        self.assertEqual(self.task.status, 'completed')
    
    def test_add_comment(self):
        """Test adding a comment to a task through the API"""
        response = self.client.post(f'/api/tasks/{self.task.id}/add_comment/', {
            'content': 'This is a test comment'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskComment.objects.count(), 1)
        self.assertEqual(TaskComment.objects.first().content, 'This is a test comment')
