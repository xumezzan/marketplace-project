from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from marketplace.models import Category, Task, Offer, Deal
from payments.models import Wallet, Transaction
from payments.services import PaymentService

User = get_user_model()


class PaymentServiceTest(TestCase):
    """Test PaymentService functionality."""
    
    def setUp(self):
        """Set up test data."""
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
        
        # Create wallet for specialist
        self.specialist_wallet, _ = Wallet.objects.get_or_create(user=self.specialist)
        
        # Create task, offer, and deal
        self.category = Category.objects.create(name='Test', slug='test')
        self.task = Task.objects.create(
            client=self.client,
            category=self.category,
            title='Test Task',
            budget_min=10000,
            budget_max=20000,
            city='Tashkent'
        )
        self.offer = Offer.objects.create(
            task=self.task,
            specialist=self.specialist,
            proposed_price=15000
        )
        self.deal = Deal.objects.create(
            task=self.task,
            offer=self.offer,
            client=self.client,
            specialist=self.specialist,
            final_price=15000,
            status=Deal.Status.IN_PROGRESS
        )
    
    def test_release_funds_calculates_commission(self):
        """Test that release_funds correctly calculates 10% commission."""
        result = PaymentService.release_funds(self.deal)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['commission_amount'], Decimal('1500.00'))  # 10% of 15000
        self.assertEqual(result['payout_amount'], Decimal('13500.00'))  # 90% of 15000
    
    def test_release_funds_updates_deal_status(self):
        """Test that release_funds updates deal status to COMPLETED."""
        PaymentService.release_funds(self.deal)
        
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.status, Deal.Status.COMPLETED)
        self.assertEqual(self.deal.commission_amount, Decimal('1500.00'))
    
    def test_release_funds_credits_specialist_wallet(self):
        """Test that release_funds credits specialist wallet with payout amount."""
        initial_balance = self.specialist_wallet.balance
        
        PaymentService.release_funds(self.deal)
        
        self.specialist_wallet.refresh_from_db()
        expected_balance = initial_balance + Decimal('13500.00')
        self.assertEqual(self.specialist_wallet.balance, expected_balance)
    
    def test_release_funds_fails_for_invalid_status(self):
        """Test that release_funds fails if deal is not IN_PROGRESS."""
        self.deal.status = Deal.Status.COMPLETED
        self.deal.save()
        
        with self.assertRaises(ValueError) as context:
            PaymentService.release_funds(self.deal)
        
        self.assertIn('IN_PROGRESS', str(context.exception))
    
    def test_refund_client_returns_full_amount(self):
        """Test that refund_client returns full amount to client wallet."""
        client_wallet, _ = Wallet.objects.get_or_create(user=self.client)
        initial_balance = client_wallet.balance
        
        result = PaymentService.refund_client(self.deal)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['refund_amount'], Decimal('15000.00'))
        
        client_wallet.refresh_from_db()
        expected_balance = initial_balance + Decimal('15000.00')
        self.assertEqual(client_wallet.balance, expected_balance)
    
    def test_refund_client_updates_deal_status(self):
        """Test that refund_client updates deal status to CANCELED."""
        Wallet.objects.get_or_create(user=self.client)
        
        PaymentService.refund_client(self.deal)
        
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.status, Deal.Status.CANCELED)
    
    def test_refund_client_fails_for_invalid_status(self):
        """Test that refund_client fails if deal is not IN_PROGRESS."""
        self.deal.status = Deal.Status.COMPLETED
        self.deal.save()
        
        with self.assertRaises(ValueError) as context:
            PaymentService.refund_client(self.deal)
        
        self.assertIn('IN_PROGRESS', str(context.exception))
    
    def test_force_pay_specialist_is_alias_for_release_funds(self):
        """Test that force_pay_specialist calls release_funds."""
        result = PaymentService.force_pay_specialist(self.deal)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['payout_amount'], Decimal('13500.00'))
        
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.status, Deal.Status.COMPLETED)


class WalletModelTest(TestCase):
    """Test Wallet model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com'
        )
        self.wallet, _ = Wallet.objects.get_or_create(user=self.user)
    
    def test_wallet_creation(self):
        """Test wallet is created with zero balance."""
        self.assertEqual(self.wallet.balance, Decimal('0.00'))
    
    def test_deposit_increases_balance(self):
        """Test deposit method increases balance."""
        self.wallet.deposit(Decimal('1000.00'))
        
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1000.00'))
    
    def test_withdraw_decreases_balance(self):
        """Test withdraw method decreases balance."""
        self.wallet.deposit(Decimal('1000.00'))
        self.wallet.withdraw(Decimal('300.00'))
        
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('700.00'))
    
    def test_withdraw_fails_with_insufficient_funds(self):
        """Test withdraw fails if insufficient funds."""
        with self.assertRaises(ValueError) as context:
            self.wallet.withdraw(Decimal('100.00'))
        
        # Error message is in Russian
        self.assertIn('средств', str(context.exception))
    
    def test_deposit_creates_transaction(self):
        """Test deposit creates a transaction record."""
        self.wallet.deposit(Decimal('1000.00'))
        
        transactions = Transaction.objects.filter(wallet=self.wallet)
        self.assertEqual(transactions.count(), 1)
        self.assertEqual(transactions.first().amount, Decimal('1000.00'))
        self.assertEqual(transactions.first().type, Transaction.Type.DEPOSIT)
