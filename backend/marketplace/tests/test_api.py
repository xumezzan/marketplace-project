from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from marketplace.models import Category, Task, Offer, Deal
from decimal import Decimal

User = get_user_model()


class TaskViewSetTest(TestCase):
    """Test TaskViewSet API endpoints."""
    
    def setUp(self):
        self.client_api = APIClient()
        self.specialist_api = APIClient()
        
        # Create users
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123',
            is_client=True
        )
        self.specialist_user = User.objects.create_user(
            username='specialist',
            email='specialist@test.com',
            password='testpass123',
            is_specialist=True
        )
        
        # Authenticate clients
        self.client_api.force_authenticate(user=self.client_user)
        self.specialist_api.force_authenticate(user=self.specialist_user)
        
        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
    
    def test_create_task_as_client(self):
        """Test client can create a task."""
        data = {
            'category': self.category.id,
            'title': 'Test Task',
            'description': 'Test description',
            'budget_min': 1000,
            'budget_max': 2000,
            'city': 'Tashkent'
        }
        response = self.client_api.post('/api/tasks/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Task')
        self.assertEqual(response.data['client'], self.client_user.id)
    
    def test_list_tasks(self):
        """Test listing tasks."""
        Task.objects.create(
            client=self.client_user,
            category=self.category,
            title='Task 1',
            budget_min=1000,
            city='Tashkent'
        )
        Task.objects.create(
            client=self.client_user,
            category=self.category,
            title='Task 2',
            budget_min=2000,
            city='Tashkent'
        )
        
        response = self.client_api.get('/api/tasks/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_task(self):
        """Test retrieving a single task."""
        task = Task.objects.create(
            client=self.client_user,
            category=self.category,
            title='Test Task',
            budget_min=1000,
            city='Tashkent'
        )
        
        response = self.client_api.get(f'/api/tasks/{task.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')


class OfferViewSetTest(TestCase):
    """Test OfferViewSet API endpoints."""
    
    def setUp(self):
        self.client_api = APIClient()
        self.specialist_api = APIClient()
        
        # Create users
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123',
            is_client=True
        )
        self.specialist_user = User.objects.create_user(
            username='specialist',
            email='specialist@test.com',
            password='testpass123',
            is_specialist=True
        )
        
        # Authenticate clients
        self.client_api.force_authenticate(user=self.client_user)
        self.specialist_api.force_authenticate(user=self.specialist_user)
        
        # Create task
        self.category = Category.objects.create(name='Test', slug='test')
        self.task = Task.objects.create(
            client=self.client_user,
            category=self.category,
            title='Test Task',
            budget_min=1000,
            budget_max=2000,
            city='Tashkent',
            status=Task.Status.PUBLISHED
        )
    
    def test_create_offer_as_specialist(self):
        """Test specialist can create an offer."""
        data = {
            'task': self.task.id,
            'proposed_price': 1500,
            'message': 'I can do this'
        }
        response = self.specialist_api.post('/api/offers/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['proposed_price'], '1500.00')
        self.assertEqual(response.data['specialist'], self.specialist_user.id)
    
    def test_client_cannot_create_offer(self):
        """Test client cannot create an offer."""
        data = {
            'task': self.task.id,
            'proposed_price': 1500,
            'message': 'I can do this'
        }
        response = self.client_api.post('/api/offers/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_offers(self):
        """Test listing offers."""
        Offer.objects.create(
            task=self.task,
            specialist=self.specialist_user,
            proposed_price=1500,
            message='Offer 1'
        )
        
        response = self.client_api.get('/api/offers/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)


class AuthenticationTest(TestCase):
    """Test authentication and permissions."""
    
    def setUp(self):
        self.client_api = APIClient()
        self.category = Category.objects.create(name='Test', slug='test')
    
    def test_unauthenticated_cannot_create_task(self):
        """Test unauthenticated user cannot create a task."""
        data = {
            'category': self.category.id,
            'title': 'Test Task',
            'description': 'Test description',
            'budget_min': 1000,
            'city': 'Tashkent'
        }
        response = self.client_api.post('/api/tasks/', data)
        
        # DRF may return 401 or 403 depending on configuration
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_unauthenticated_can_list_tasks(self):
        """Test unauthenticated user can list tasks (read-only)."""
        response = self.client_api.get('/api/tasks/')
        
        # Should be allowed (IsAuthenticatedOrReadOnly)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
