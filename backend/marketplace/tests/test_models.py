from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from marketplace.models import Category, Task, Offer, Deal, Review, Dispute
from payments.models import Wallet

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model functionality."""
    
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='client1',
            email='client1@test.com',
            password='testpass123',
            is_client=True
        )
        self.specialist_user = User.objects.create_user(
            username='specialist1',
            email='specialist1@test.com',
            password='testpass123',
            is_specialist=True
        )
    
    def test_user_creation(self):
        """Test user can be created with roles."""
        self.assertEqual(self.client_user.username, 'client1')
        self.assertTrue(self.client_user.is_client)
        self.assertFalse(self.client_user.is_specialist)
    
    def test_user_can_have_both_roles(self):
        """Test user can be both client and specialist."""
        dual_user = User.objects.create_user(
            username='dual',
            email='dual@test.com',
            password='testpass123',
            is_client=True,
            is_specialist=True
        )
        self.assertTrue(dual_user.is_client)
        self.assertTrue(dual_user.is_specialist)
    
    def test_user_string_representation(self):
        """Test user __str__ method."""
        self.assertIn('client1', str(self.client_user))


class TaskModelTest(TestCase):
    """Test Task model functionality."""
    
    def setUp(self):
        self.client = User.objects.create_user(
            username='client',
            email='client@test.com',
            is_client=True
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.task = Task.objects.create(
            client=self.client,
            category=self.category,
            title='Test Task',
            description='Test description',
            budget_min=1000,
            budget_max=2000,
            city='Tashkent',
            status=Task.Status.PUBLISHED
        )
    
    def test_task_creation(self):
        """Test task can be created."""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.status, Task.Status.PUBLISHED)
        self.assertEqual(self.task.moderation_status, Task.ModerationStatus.PENDING)
    
    def test_can_receive_offers(self):
        """Test can_receive_offers method."""
        self.assertTrue(self.task.can_receive_offers())
        
        self.task.status = Task.Status.COMPLETED
        self.task.save()
        self.assertFalse(self.task.can_receive_offers())
    
    def test_budget_display(self):
        """Test budget_display property."""
        display = self.task.budget_display
        self.assertIn('1000', display)
        self.assertIn('2000', display)


class OfferModelTest(TestCase):
    """Test Offer model functionality."""
    
    def setUp(self):
        self.client = User.objects.create_user(
            username='client',
            email='client@test.com',
            is_client=True
        )
        self.specialist = User.objects.create_user(
            username='specialist',
            email='specialist@test.com',
            is_specialist=True
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.task = Task.objects.create(
            client=self.client,
            category=self.category,
            title='Test Task',
            budget_min=1000,
            budget_max=2000,
            city='Tashkent',
            status=Task.Status.PUBLISHED
        )
        self.offer = Offer.objects.create(
            task=self.task,
            specialist=self.specialist,
            proposed_price=1500,
            message='I can do this',
            status=Offer.Status.PENDING
        )
    
    def test_offer_creation(self):
        """Test offer can be created."""
        self.assertEqual(self.offer.proposed_price, 1500)
        self.assertEqual(self.offer.status, Offer.Status.PENDING)
    
    def test_can_be_accepted(self):
        """Test can_be_accepted method."""
        self.assertTrue(self.offer.can_be_accepted())
        
        self.offer.status = Offer.Status.REJECTED
        self.offer.save()
        self.assertFalse(self.offer.can_be_accepted())
    
    def test_accept_offer(self):
        """Test accept method."""
        self.offer.accept()
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, Offer.Status.ACCEPTED)
        
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)


class DealModelTest(TestCase):
    """Test Deal model functionality."""
    
    def setUp(self):
        self.client = User.objects.create_user(
            username='client',
            email='client@test.com',
            is_client=True
        )
        self.specialist = User.objects.create_user(
            username='specialist',
            email='specialist@test.com',
            is_specialist=True
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.task = Task.objects.create(
            client=self.client,
            category=self.category,
            title='Test Task',
            budget_min=1000,
            budget_max=2000,
            city='Tashkent'
        )
        self.offer = Offer.objects.create(
            task=self.task,
            specialist=self.specialist,
            proposed_price=1500
        )
        self.deal = Deal.objects.create(
            task=self.task,
            offer=self.offer,
            client=self.client,
            specialist=self.specialist,
            final_price=1500,
            status=Deal.Status.PENDING
        )
    
    def test_deal_creation(self):
        """Test deal can be created."""
        self.assertEqual(self.deal.final_price, 1500)
        self.assertEqual(self.deal.status, Deal.Status.PENDING)
    
    def test_deal_status_transitions(self):
        """Test deal status can transition."""
        self.deal.status = Deal.Status.IN_PROGRESS
        self.deal.save()
        self.assertEqual(self.deal.status, Deal.Status.IN_PROGRESS)


class DisputeModelTest(TestCase):
    """Test Dispute model functionality."""
    
    def setUp(self):
        self.client = User.objects.create_user(
            username='client',
            email='client@test.com',
            is_client=True
        )
        self.specialist = User.objects.create_user(
            username='specialist',
            email='specialist@test.com',
            is_specialist=True
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.task = Task.objects.create(
            client=self.client,
            category=self.category,
            title='Test Task',
            budget_min=1000,
            city='Tashkent'
        )
        self.offer = Offer.objects.create(
            task=self.task,
            specialist=self.specialist,
            proposed_price=1500
        )
        self.deal = Deal.objects.create(
            task=self.task,
            offer=self.offer,
            client=self.client,
            specialist=self.specialist,
            final_price=1500,
            status=Deal.Status.IN_PROGRESS
        )
    
    def test_dispute_creation(self):
        """Test dispute can be created."""
        dispute = Dispute.objects.create(
            deal=self.deal,
            initiator=self.client,
            reason='Not satisfied',
            description='Work not completed'
        )
        self.assertEqual(dispute.status, Dispute.Status.OPEN)
        self.assertEqual(dispute.resolution, Dispute.Resolution.NONE)
    
    def test_dispute_resolution(self):
        """Test dispute can be resolved."""
        dispute = Dispute.objects.create(
            deal=self.deal,
            initiator=self.client,
            reason='Not satisfied',
            description='Work not completed'
        )
        dispute.status = Dispute.Status.RESOLVED
        dispute.resolution = Dispute.Resolution.REFUND_CLIENT
        dispute.save()
        
        self.assertEqual(dispute.status, Dispute.Status.RESOLVED)
        self.assertEqual(dispute.resolution, Dispute.Resolution.REFUND_CLIENT)
