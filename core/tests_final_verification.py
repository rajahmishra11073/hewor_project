from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Freelancer, ServiceOrder
from django.urls import reverse
from django.utils import timezone
import datetime

class FinalSystemTest(TestCase):
    def setUp(self):
        # 1. Setup Admin & Client
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client_user = User.objects.create_user('testclient', 'client@test.com', 'password')
        self.client.login(username='admin', password='password')

        # 2. Create a Freelancer with Full Profile
        self.freelancer = Freelancer.objects.create(
            user=self.admin, # Using admin user just for FK constraint
            name="Super Freelancer",
            freelancer_id="F-999",
            payment_details="Bank: HDFC 123456",
            phone="9876543210"
        )
        
        # 3. Create a Service Order
        self.order = ServiceOrder.objects.create(
            user=self.client_user,
            title="Complex Research Project",
            service_type="consultation",
            description="Needs deep dive.",
            status="in_progress"
        )
        
        # 4. Assign Order to Freelancer (Simulating 'Assign' view logic)
        self.order.freelancer = self.freelancer
        self.order.assigned_at = timezone.now()
        self.order.freelancer_deadline = timezone.now() + datetime.timedelta(days=1)
        self.order.freelancer_status = 'pending_acceptance'
        self.order.is_freelancer_paid = False
        self.order.save()
        
    def test_manage_works_view_integrity(self):
        """
        Verifies that the new Manage Works table renders all critical business data.
        """
        response = self.client.get(reverse('manage_freelancer_works'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # CHECK 1: Freelancer Identity
        self.assertIn("Super Freelancer", content, "Freelancer Name missing")
        self.assertIn("F-999", content, "Freelancer ID missing")
        
        # CHECK 2: Client Info
        self.assertIn("testclient", content, "Forwarded Client Name missing")
        
        # CHECK 3: Project Details
        self.assertIn("Complex Research Project", content, "Task Title missing")
        
        # CHECK 4: Payment & Status
        self.assertIn("Bank: HDFC 123456", content, "Payment Options missing")
        self.assertIn("Pending Acceptance", content, "Status Badge missing") # Django renders choice display
        self.assertIn("UNPAID", content, "Paid Status Badge missing")
        
        # CHECK 5: Actions
        self.assertIn("Verify & Send to Client", content, "Send to Client button missing")
        self.assertIn("Chat with Freelancer", content, "Chat button missing")

        print("\n\nSUCCESS: All critical fields verified in the Manage Freelancers Table.")
