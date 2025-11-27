from django.test import TestCase
from django.contrib.auth import get_user_model
from chat.models import Conversation, Message
from notifications.models import Notification
from users.models import SpecialistProfile, PortfolioItem
from wallet.models import Wallet, Transaction
from wallet.services import EscrowService
from orders.models import Order
from services.models import Category
from decimal import Decimal

User = get_user_model()

class NewFeaturesTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(phone_number='+998901234567', password='password')
        self.specialist_user = User.objects.create_user(phone_number='+998909876543', password='password', role='specialist')
        self.specialist_profile = SpecialistProfile.objects.create(user=self.specialist_user)
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        
        # Wallet setup
        self.client_wallet = Wallet.objects.create(user=self.client_user, balance=100000)
        self.specialist_wallet = Wallet.objects.create(user=self.specialist_user, balance=0)

    def test_chat_flow(self):
        # Start conversation
        conv = Conversation.objects.create(participant1=self.client_user, participant2=self.specialist_user)
        
        # Send message
        msg = Message.objects.create(conversation=conv, sender=self.client_user, content="Hello")
        
        self.assertEqual(conv.messages.count(), 1)
        self.assertFalse(msg.is_read)
        
    def test_notification_flow(self):
        notif = Notification.objects.create(user=self.client_user, title="Test", message="Body")
        self.assertFalse(notif.is_read)
        
    def test_portfolio_flow(self):
        item = PortfolioItem.objects.create(
            specialist=self.specialist_profile,
            title="My Work",
            description="Good work"
        )
        self.assertEqual(self.specialist_profile.portfolio_items.count(), 1)
        
    def test_escrow_flow(self):
        order = Order.objects.create(
            client=self.client_user,
            category=self.category,
            description="Fix something",
            is_safe_deal=True
        )
        
        # Lock funds
        EscrowService.lock_funds(self.client_user, 50000, order)
        
        self.client_wallet.refresh_from_db()
        self.assertEqual(self.client_wallet.balance, 50000)
        self.assertEqual(Transaction.objects.filter(transaction_type=Transaction.Type.ESCROW_LOCK).count(), 1)
        
        # Mock accepted response for release
        from orders.models import OrderResponse
        OrderResponse.objects.create(
            order=order,
            specialist=self.specialist_user,
            price_proposal=50000,
            message="I will do it",
            is_accepted=True
        )
        
        # Release funds
        EscrowService.release_funds(order, self.specialist_user)
        
        self.specialist_wallet.refresh_from_db()
        self.assertEqual(self.specialist_wallet.balance, 50000)
