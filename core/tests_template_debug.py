from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Freelancer, ServiceOrder, FreelancerChat
from django.utils import timezone
import datetime
from django.urls import reverse

class FreelancerSystemTest(TestCase):
    def setUp(self):
        # Create Admin
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client.login(username='admin', password='password')

        # Create Freelancer
        self.freelancer_user = User.objects.create_user('freelancer', 'free@test.com', 'password')
        self.freelancer = Freelancer.objects.create(
            user=self.freelancer_user,
            name="Test Freelancer",
            freelancer_id="F001",
            phone="1234567890"
        )
        
        # Create Order
        self.order = ServiceOrder.objects.create(
            user=self.admin_user,
            title="Test Order",
            service_type="data_entry",
            description="Test Description"
        )

    def test_assignment_logic(self):
        # Assign Order via View Logic (simulated by updating model directly for unit test speed, 
        # but view test is better. Let's test the view.)
        
        url = reverse('order_panel_assign_freelancer', args=[self.order.id])
        response = self.client.post(url, {
            'freelancer_id': self.freelancer.id,
            'freelancer_description': 'Work hard'
        })
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.freelancer, self.freelancer)
        self.assertEqual(self.order.freelancer_status, 'pending_acceptance')
        self.assertIsNotNone(self.order.assigned_at)
        
        # Check Deadline (approx 2 days)
        self.assertTrue(self.order.freelancer_deadline > timezone.now() + datetime.timedelta(days=1))

    def test_freelancer_accept_order(self):
        # Setup: Assign first
        self.order.freelancer = self.freelancer
        self.order.assigned_at = timezone.now()
        self.order.freelancer_status = 'pending_acceptance'
        self.order.save()
        
        # Login as Freelancer
        self.client.login(username='freelancer', password='password')
        
        url = reverse('freelancer_accept_order', args=[self.order.id])
        response = self.client.get(url)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.freelancer_status, 'accepted')

    def test_freelancer_timeout_logic(self):
        # Setup: Assign OLD date (1 hour ago)
        self.order.freelancer = self.freelancer
        self.order.assigned_at = timezone.now() - datetime.timedelta(minutes=45)
        self.order.freelancer_status = 'pending_acceptance'
        self.order.save()
        
        # Login as Freelancer
        self.client.login(username='freelancer', password='password')
        
        url = reverse('freelancer_accept_order', args=[self.order.id])
        response = self.client.get(url) # Should fail/set timeout
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.freelancer_status, 'timeout')

    def test_freelancer_dashboard_rendering(self):
        # Setup: Assign and Accept
        self.order.freelancer = self.freelancer
        self.order.assigned_at = timezone.now()
        self.order.freelancer_status = 'accepted'
        self.order.save()
        
        self.client.login(username='freelancer', password='password')
        response = self.client.get(reverse('freelancer_dashboard'))
        
        content = response.content.decode('utf-8')
        
        # Check if raw tag is present (Failure case)
        if "{{ order.assigned_at" in content:
            print("FAILURE: Found raw tag {{ order.assigned_at... }} in content!")
            # print(content) # Debug
            self.fail("Template not rendering tags correctly.")
        
        # Check if rendered correctly (Success case)
        if "Assigned:" in content:
             # It prints month, e.g. "Jan"
             current_month = timezone.now().strftime("%b")
             if current_month not in content:
                 print(f"WARNING: Month {current_month} not found in content.")

    def test_freelancer_chat(self):
        self.order.freelancer = self.freelancer
        self.order.save()
        
        # Admin sends message
        FreelancerChat.objects.create(
            order=self.order,
            sender=self.admin_user,
            message="Hello Freelancer"
        )
        
        self.assertTrue(FreelancerChat.objects.filter(message="Hello Freelancer").exists())
