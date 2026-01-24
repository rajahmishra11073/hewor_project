from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Freelancer
from django.urls import reverse

class FreelancerListDebugTest(TestCase):
    def setUp(self):
        # Create Admin
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client.login(username='admin', password='password')

        # Create Freelancer to test the card rendering loop
        self.freelancer = Freelancer.objects.create(
            user=self.admin, # reusing admin user for simplicity
            name="Test Freelancer",
            freelancer_id="F001",
            address="123 Test St",
            profession="Tester"
        )
        
    def test_freelancer_list_load(self):
        url = reverse('order_panel_freelancers')
        response = self.client.get(url)
        
        if response.status_code != 200:
            print(f"Error Content: {response.content.decode('utf-8')}")
            
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Check if ID tag rendered correctly (no raw braces)
        if "{{ f.freelancer_id" in content:
            self.fail("Found raw {{ f.freelancer_id }} tag!")
            
        # Check if Link exists
        expected_url = reverse('order_panel_freelancer_detail', args=[self.freelancer.id])
        if expected_url not in content:
            print(f"WARNING: Link to {expected_url} not found.")

        print("Success: Freelancer List loaded with status 200")
