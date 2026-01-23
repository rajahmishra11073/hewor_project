from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ServiceOrder, Freelancer, OrderFile, FreelancerChat
from django.core.files.uploadedfile import SimpleUploadedFile

class FreelancerPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Setup Admin/Order User
        self.admin_user = User.objects.create_user(username='Hewor.order', password='password123')
        
        # 2. Setup Freelancer User & Profile
        self.freelancer_user = User.objects.create_user(username='FL001', password='password123')
        self.freelancer = Freelancer.objects.create(
            user=self.freelancer_user,
            name="Alice Dev",
            freelancer_id="FL001",
            profession="Developer",
            expertise="Django"
        )
        
        # 3. Setup Order
        self.client_user = User.objects.create_user(username='client', password='password123')
        self.order = ServiceOrder.objects.create(
            user=self.client_user,
            title="Test Project",
            service_type="web_scraping",
            description="Scrape data",
            status='pending'
        )
        
        self.portal_login_url = reverse('freelancer_login')
        self.portal_dashboard_url = reverse('freelancer_dashboard')
        self.portal_detail_url = reverse('freelancer_order_detail', args=[self.order.id])
        self.assign_url = reverse('order_panel_assign_freelancer', args=[self.order.id])

    def test_admin_assign_freelancer(self):
        self.client.login(username='Hewor.order', password='password123')
        roadmap = SimpleUploadedFile("roadmap.pdf", b"steps")
        
        response = self.client.post(self.assign_url, {
            'freelancer_id': self.freelancer.id,
            'freelancer_description': 'Do this tasks',
            'freelancer_roadmap': roadmap
        })
        
        self.assertRedirects(response, reverse('order_panel_dashboard'))
        self.order.refresh_from_db()
        self.assertEqual(self.order.freelancer, self.freelancer)
        self.assertEqual(self.order.freelancer_description, 'Do this tasks')
        self.assertTrue(self.order.freelancer_roadmap)

    def test_freelancer_login_and_access(self):
        # Assign first
        self.order.freelancer = self.freelancer
        self.order.save()
        
        # Login
        response = self.client.post(self.portal_login_url, {
            'username': 'FL001',
            'password': 'password123'
        })
        self.assertRedirects(response, self.portal_dashboard_url)
        
        # Dashboard Access
        response = self.client.get(self.portal_dashboard_url)
        self.assertContains(response, "Test Project")
        
        # Detail Access
        response = self.client.get(self.portal_detail_url)
        self.assertContains(response, "Test Project")
        
    def test_freelancer_upload_work(self):
        self.order.freelancer = self.freelancer
        self.order.save()
        self.client.login(username='FL001', password='password123')
        
        work_file = SimpleUploadedFile("final_code.zip", b"code")
        response = self.client.post(self.portal_detail_url, {
            'action': 'upload_work',
            'files': [work_file]
        })
        
        self.assertRedirects(response, self.portal_detail_url)
        self.assertTrue(OrderFile.objects.filter(order=self.order, file_type='freelancer_upload').exists())

    def test_freelancer_chat(self):
        self.order.freelancer = self.freelancer
        self.order.save()
        self.client.login(username='FL001', password='password123')
        
        response = self.client.post(self.portal_detail_url, {
            'action': 'send_message',
            'message': 'Work is done'
        })
        
        self.assertRedirects(response, self.portal_detail_url)
        self.assertTrue(FreelancerChat.objects.filter(order=self.order, message='Work is done', sender=self.freelancer_user).exists())
