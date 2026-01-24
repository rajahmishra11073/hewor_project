from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Freelancer, ServiceOrder
from django.urls import reverse
from django.utils import timezone

class ManageFreelancersTableTest(TestCase):
    def setUp(self):
        # Create a user and admin
        self.user = User.objects.create_user('client', 'client@test.com', 'password')
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client.login(username='admin', password='password')

        # Create Freelancer
        self.freelancer = Freelancer.objects.create(
            user=self.admin, # Reusing for simplicity
            name="Test Freelancer",
            freelancer_id="F123",
            payment_details="UPI: 123@upi"
        )
        
        # Create Assigned Order
        self.order = ServiceOrder.objects.create(
            user=self.user,
            title="Test Project Alpha",
            service_type="presentation",
            description="Test Desc",
            freelancer=self.freelancer,
            assigned_at=timezone.now(),
            freelancer_deadline=timezone.now(),
            freelancer_status='accepted',
            is_freelancer_paid=True
        )
        
    def test_manage_works_table_load(self):
        url = reverse('manage_freelancer_works')
        response = self.client.get(url)
        
        if response.status_code != 200:
            print(f"Error Content: {response.content.decode('utf-8')[:500]}...")
            
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Verify Columns
        self.assertIn("Test Project Alpha", content)
        self.assertIn("F123", content)
        self.assertIn("UPI: 123@upi", content)
        self.assertIn("PAID", content) # Checking paid status badge
        self.assertIn("Accepted", content) # Checking status display

        print("Success: Manage Freelancers Table loaded with all columns.")
