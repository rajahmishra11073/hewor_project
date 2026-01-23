from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ServiceOrder, OrderFile, Freelancer
from django.core.files.uploadedfile import SimpleUploadedFile

class OrderPanelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='Hewor.order', password='password123')
        self.client_user = User.objects.create_user(username='client', password='password123')
        self.order = ServiceOrder.objects.create(
            user=self.client_user,
            title="Test Project",
            service_type="Test Service",
            description="Details",
            status='pending'
        )
        self.login_url = reverse('order_panel_login')
        self.dashboard_url = reverse('order_panel_dashboard')
        self.upload_url = reverse('order_panel_upload', args=[self.order.id])
        self.mark_delivered_url = reverse('order_panel_mark_delivered', args=[self.order.id])
        self.assign_freelancer_url = reverse('order_panel_assign_freelancer', args=[self.order.id])

    def test_login_redirect(self):
        response = self.client.get(self.dashboard_url)
        expected_url = f"{self.login_url}?next={self.dashboard_url}"
        self.assertRedirects(response, expected_url)

    def test_dashboard_access(self):
        self.client.login(username='Hewor.order', password='password123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")
        self.assertTemplateUsed(response, 'core/order_panel_dashboard.html')

    def test_upload_file(self):
        self.client.login(username='Hewor.order', password='password123')
        file = SimpleUploadedFile("delivery.txt", b"content")
        response = self.client.post(self.upload_url, {
            'file_upload': [file],
            'file_type': 'delivery'
        })
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(OrderFile.objects.filter(order=self.order, original_filename="delivery.txt", file_type='delivery').exists())

    def test_mark_delivered(self):
        self.client.login(username='Hewor.order', password='password123')
        response = self.client.post(self.mark_delivered_url)
        self.assertRedirects(response, self.dashboard_url)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_assign_freelancer(self):
        self.client.login(username='Hewor.order', password='password123')
        response = self.client.post(self.assign_freelancer_url, {'freelancer_name': 'John Doe'})
        self.assertRedirects(response, self.dashboard_url)
        self.order.refresh_from_db()
        self.assertEqual(self.order.freelancer, 'John Doe')

    def test_create_and_delete_freelancer(self):
        self.client.login(username='Hewor.order', password='password123')
        url = reverse('order_panel_freelancers')
        
        # Create
        response = self.client.post(url, {
            'name': 'Jane Doe',
            'freelancer_id': 'FL123',
            'profession': 'Developer',
            'expertise': 'Python, Django'
        })
        self.assertRedirects(response, url)
        self.assertTrue(Freelancer.objects.filter(freelancer_id='FL123').exists())
        
        # Delete
        freelancer = Freelancer.objects.get(freelancer_id='FL123')
        delete_url = reverse('order_panel_delete_freelancer', args=[freelancer.id])
        response = self.client.post(delete_url)
        self.assertRedirects(response, url)
        self.assertFalse(Freelancer.objects.filter(freelancer_id='FL123').exists())
