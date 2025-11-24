import json
import base64
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from marketplace.models import Deal, Task, Category, SpecialistProfile, ClientProfile, Offer
from payments.models import PaymeTransaction

User = get_user_model()

@override_settings(PAYME_LOGIN='Paycom', PAYME_KEY='password')
class PaymeIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('payments_api:payme')
        
        # Create users
        self.client_user = User.objects.create_user(username='client', email='client@example.com', password='password', is_client=True)
        ClientProfile.objects.create(user=self.client_user)
        
        self.specialist_user = User.objects.create_user(username='specialist', email='specialist@example.com', password='password', is_specialist=True)
        SpecialistProfile.objects.create(user=self.specialist_user)
        
        # Create task and deal
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.task = Task.objects.create(
            client=self.client_user,
            title='Test Task',
            category=self.category,
            budget_min=100000
        )
        
        self.offer = Offer.objects.create(
            task=self.task,
            specialist=self.specialist_user,
            proposed_price=100000,
            status=Offer.Status.ACCEPTED
        )
        
        self.deal = Deal.objects.create(
            task=self.task,
            offer=self.offer,
            client=self.client_user,
            specialist=self.specialist_user,
            final_price=100000,
            status=Deal.Status.PENDING
        )
        
        # Auth header
        # Assuming no password check for now as per implementation
        credentials = 'Paycom:password'
        self.auth_header = 'Basic ' + base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    def test_check_perform_transaction(self):
        payload = {
            "method": "CheckPerformTransaction",
            "params": {
                "amount": 10000000, # 100 000 sum * 100 tiyin
                "account": {
                    "deal_id": self.deal.id
                }
            },
            "id": 123
        }
        
        response = self.client.post(
            self.url,
            data=payload,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('result', data)
        self.assertTrue(data['result']['allow'])

    def test_create_transaction(self):
        payload = {
            "method": "CreateTransaction",
            "params": {
                "id": "test_trans_id_1",
                "time": 1234567890000,
                "amount": 10000000,
                "account": {
                    "deal_id": self.deal.id
                }
            },
            "id": 124
        }
        
        response = self.client.post(
            self.url,
            data=payload,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('result', data)
        self.assertEqual(data['result']['state'], 1)
        
        # Verify DB
        trans = PaymeTransaction.objects.get(payme_id="test_trans_id_1")
        self.assertEqual(trans.amount, 10000000)
        self.assertEqual(trans.deal, self.deal)

    def test_perform_transaction(self):
        import time
        current_time = int(time.time() * 1000)
        
        # First create
        PaymeTransaction.objects.create(
            payme_id="test_trans_id_2",
            time=current_time,
            amount=10000000,
            account={"deal_id": self.deal.id},
            state=1,
            deal=self.deal,
            create_time=current_time
        )
        
        payload = {
            "method": "PerformTransaction",
            "params": {
                "id": "test_trans_id_2"
            },
            "id": 125
        }
        
        response = self.client.post(
            self.url,
            data=payload,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('result', data)
        self.assertEqual(data['result']['state'], 2)
        
        # Verify Deal status
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.status, Deal.Status.IN_PROGRESS)
