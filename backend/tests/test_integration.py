from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from marketplace.models import Category, Task, Offer, Deal
from payments.models import Wallet
from payments.services import PaymentService

User = get_user_model()


class TaskFlowIntegrationTest(TestCase):
    """Test complete task creation → offer → deal flow."""
    
    def setUp(self):
        # Create users
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            is_client=True
        )
        self.specialist_user = User.objects.create_user(
            username='specialist',
            email='specialist@test.com',
            is_specialist=True
        )
        
        # Create category
        self.category = Category.objects.create(name='Test', slug='test')
        
        # Create wallets
        self.client_wallet, _ = Wallet.objects.get_or_create(user=self.client_user)
        self.specialist_wallet, _ = Wallet.objects.get_or_create(user=self.specialist_user)
    
    def test_complete_task_flow(self):
        """Test complete flow from task creation to completion."""
        # 1. Client creates a task
        task = Task.objects.create(
            client=self.client_user,
            category=self.category,
            title='Fix my laptop',
            description='Screen is broken',
            budget_min=10000,
            budget_max=20000,
            city='Tashkent',
            status=Task.Status.PUBLISHED
        )
        self.assertEqual(task.status, Task.Status.PUBLISHED)
        
        # 2. Specialist creates an offer
        offer = Offer.objects.create(
            task=task,
            specialist=self.specialist_user,
            proposed_price=15000,
            message='I can fix it'
        )
        self.assertEqual(offer.status, Offer.Status.PENDING)
        
        # 3. Client accepts the offer
        offer.accept()
        offer.refresh_from_db()
        task.refresh_from_db()
        
        self.assertEqual(offer.status, Offer.Status.ACCEPTED)
        self.assertEqual(task.status, Task.Status.IN_PROGRESS)
        
        # 4. Deal is created
        deal = Deal.objects.create(
            task=task,
            offer=offer,
            client=self.client_user,
            specialist=self.specialist_user,
            final_price=15000,
            status=Deal.Status.IN_PROGRESS
        )
        self.assertEqual(deal.final_price, 15000)
        
        # 5. Work is completed and funds are released
        initial_balance = self.specialist_wallet.balance
        result = PaymentService.release_funds(deal)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['commission_amount'], Decimal('1500.00'))  # 10%
        self.assertEqual(result['payout_amount'], Decimal('13500.00'))  # 90%
        
        # 6. Verify deal and wallet updates
        deal.refresh_from_db()
        self.specialist_wallet.refresh_from_db()
        
        self.assertEqual(deal.status, Deal.Status.COMPLETED)
        self.assertEqual(self.specialist_wallet.balance, initial_balance + Decimal('13500.00'))


class PaymentFlowIntegrationTest(TestCase):
    """Test payment → escrow → completion → withdrawal flow."""
    
    def setUp(self):
        # Create users
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            is_client=True
        )
        self.specialist_user = User.objects.create_user(
            username='specialist',
            email='specialist@test.com',
            is_specialist=True
        )
        
        # Create wallets
        self.client_wallet, _ = Wallet.objects.get_or_create(user=self.client_user)
        self.specialist_wallet, _ = Wallet.objects.get_or_create(user=self.specialist_user)
        
        # Create task, offer, and deal
        self.category = Category.objects.create(name='Test', slug='test')
        self.task = Task.objects.create(
            client=self.client_user,
            category=self.category,
            title='Test Task',
            budget_min=10000,
            city='Tashkent'
        )
        self.offer = Offer.objects.create(
            task=self.task,
            specialist=self.specialist_user,
            proposed_price=15000
        )
        self.deal = Deal.objects.create(
            task=self.task,
            offer=self.offer,
            client=self.client_user,
            specialist=self.specialist_user,
            final_price=15000,
            status=Deal.Status.IN_PROGRESS
        )
    
    def test_payment_and_withdrawal_flow(self):
        """Test complete payment flow with withdrawal."""
        # 1. Release funds (simulates payment completion)
        initial_balance = self.specialist_wallet.balance
        PaymentService.release_funds(self.deal)
        
        self.specialist_wallet.refresh_from_db()
        new_balance = self.specialist_wallet.balance
        
        # Specialist should have 90% of the deal price
        self.assertEqual(new_balance, initial_balance + Decimal('13500.00'))
        
        # 2. Specialist withdraws funds
        withdraw_amount = Decimal('5000.00')
        self.specialist_wallet.withdraw(withdraw_amount)
        
        self.specialist_wallet.refresh_from_db()
        final_balance = self.specialist_wallet.balance
        
        self.assertEqual(final_balance, new_balance - withdraw_amount)
        self.assertEqual(final_balance, Decimal('8500.00'))


class DisputeFlowIntegrationTest(TestCase):
    """Test dispute creation and resolution flow."""
    
    def setUp(self):
        # Create users
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            is_client=True
        )
        self.specialist_user = User.objects.create_user(
            username='specialist',
            email='specialist@test.com',
            is_specialist=True
        )
        
        # Create wallets
        self.client_wallet, _ = Wallet.objects.get_or_create(user=self.client_user)
        self.specialist_wallet, _ = Wallet.objects.get_or_create(user=self.specialist_user)
        
        # Create task, offer, and deal
        self.category = Category.objects.create(name='Test', slug='test')
        self.task = Task.objects.create(
            client=self.client_user,
            category=self.category,
            title='Test Task',
            budget_min=10000,
            city='Tashkent'
        )
        self.offer = Offer.objects.create(
            task=self.task,
            specialist=self.specialist_user,
            proposed_price=15000
        )
        self.deal = Deal.objects.create(
            task=self.task,
            offer=self.offer,
            client=self.client_user,
            specialist=self.specialist_user,
            final_price=15000,
            status=Deal.Status.IN_PROGRESS
        )
    
    def test_dispute_with_refund(self):
        """Test dispute resolution with client refund."""
        # 1. Client creates a dispute
        from marketplace.models import Dispute
        
        dispute = Dispute.objects.create(
            deal=self.deal,
            initiator=self.client_user,
            reason='Work not completed',
            description='Specialist did not finish the work'
        )
        self.assertEqual(dispute.status, Dispute.Status.OPEN)
        
        # 2. Admin resolves dispute in favor of client (refund)
        initial_balance = self.client_wallet.balance
        result = PaymentService.refund_client(self.deal)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['refund_amount'], Decimal('15000.00'))
        
        # 3. Verify refund
        self.client_wallet.refresh_from_db()
        self.deal.refresh_from_db()
        
        self.assertEqual(self.client_wallet.balance, initial_balance + Decimal('15000.00'))
        self.assertEqual(self.deal.status, Deal.Status.CANCELED)
