from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from marketplace.models import Task, Category, SpecialistProfile, Offer, Deal, Review
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

class CoreFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Category
        self.category = Category.objects.create(
            name='Home Repairs',
            slug='home-repairs',
            description='General home repair services'
        )
        
        # Create Client
        self.client_user = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='password123',
            is_client=True,
            is_specialist=False
        )
        
        # Create Specialist
        self.specialist_user = User.objects.create_user(
            username='specialist',
            email='specialist@example.com',
            password='password123',
            is_client=False,
            is_specialist=True
        )
        self.specialist_profile = SpecialistProfile.objects.create(
            user=self.specialist_user,
            description="Expert Plumber",
            hourly_rate=50.00
        )
        self.specialist_profile.categories.add(self.category)

    def test_full_deal_flow(self):
        """
        Test the complete flow: Task Creation -> Offer -> Acceptance -> Completion
        """
        # 1. Client Creates Task
        self.client.force_login(self.client_user)
        task_data = {
            'title': 'Fix leaking pipe',
            'description': 'Kitchen sink pipe is leaking',
            'category': self.category.id,
            'city': 'Tashkent',
            'budget_min': 50.00,
            'budget_max': 100.00,
            'preferred_date': (timezone.now() + timezone.timedelta(days=2)).date()
        }
        response = self.client.post(reverse('marketplace:task_create'), task_data)
        if response.status_code == 200:
            print(response.context['form'].errors)
        self.assertEqual(response.status_code, 302) # Should redirect to detail
        
        task = Task.objects.get(title='Fix leaking pipe')
        # Manually publish for test flow
        task.status = Task.Status.PUBLISHED
        task.save()
        self.assertEqual(task.status, Task.Status.PUBLISHED)
        
        # 2. Specialist Finds Task (Search/List)
        self.client.logout()
        self.client.force_login(self.specialist_user)
        
        # Verify task appears in list
        response = self.client.get(reverse('marketplace:tasks_list'))
        self.assertContains(response, 'Fix leaking pipe')
        
        # 3. Specialist Makes Offer
        response = self.client.post(reverse('marketplace:task_detail', kwargs={'pk': task.id}), {
            'proposed_price': '90.00',
            'message': 'I can fix this today.'
        })
        self.assertEqual(response.status_code, 302) # Redirects back to detail
        
        offer = Offer.objects.get(task=task, specialist=self.specialist_user)
        self.assertEqual(offer.proposed_price, 90.00)
        self.assertEqual(offer.status, Offer.Status.PENDING)
        
        # 4. Client Accepts Offer
        self.client.logout()
        self.client.force_login(self.client_user)
        
        response = self.client.post(reverse('marketplace:accept_offer', kwargs={'offer_id': offer.id}))
        self.assertEqual(response.status_code, 302)
        
        # Verify Deal Created
        deal = Deal.objects.get(task=task)
        self.assertEqual(deal.specialist, self.specialist_user)
        self.assertEqual(deal.final_price, 90.00)
        self.assertEqual(deal.status, Deal.Status.PENDING)
        
        # Verify Task Status
        task.refresh_from_db()
        # Task status might be updated to IN_PROGRESS or similar depending on logic.
        # Let's check AcceptOfferView logic if I can recall or just check deal existence.
        
        # 5. Mark Deal Paid (Client)
        response = self.client.post(reverse('marketplace:mark_deal_paid', kwargs={'deal_id': deal.id}))
        self.assertEqual(response.status_code, 302)
        
        deal.refresh_from_db()
        self.assertEqual(deal.status, Deal.Status.PAID)
        
        # 6. Mark Deal Completed (Client)
        response = self.client.post(reverse('marketplace:mark_deal_completed', kwargs={'deal_id': deal.id}))
        self.assertEqual(response.status_code, 302)
        
        deal.refresh_from_db()
        self.assertEqual(deal.status, Deal.Status.COMPLETED)
        
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.COMPLETED)

    def test_specialist_search(self):
        """
        Test that users can find specialists.
        """
        response = self.client.get(reverse('marketplace:specialist_list'), {'q': 'Plumber'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'specialist')
