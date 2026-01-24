from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Freelancer, ServiceOrder
from django.urls import reverse

class OrderPanelDebugTest(TestCase):
    def setUp(self):
        # Create Admin
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client.login(username='admin', password='password')

        # Create Freelancer (to populate the select loop)
        self.freelancer = Freelancer.objects.create(
            user=self.admin, # user just needs to exist
            name="Test Freelancer",
            freelancer_id="F001"
        )
        
        # Create Order
        self.order = ServiceOrder.objects.create(
            user=self.admin,
            title="Test Order",
            service_type="data_entry",
            description="Test Description",
            freelancer=self.freelancer # To trigger the {% if order.freelancer.id == f.id %} check
        )

    def test_dashboard_load(self):
        url = reverse('order_panel_dashboard')
        response = self.client.get(url)
        
        if response.status_code != 200:
            print(f"Error Content: {response.content.decode('utf-8')}")
            
        self.assertEqual(response.status_code, 200)
        print("Success: Dashboard loaded with status 200")
