from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from unittest.mock import patch

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.verify_otp_url = reverse('verify_otp')
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
        
        # Create a dummy user for login tests
        self.user = User.objects.create_user(
            username='8797456730',
            email='test@example.com',
            password='password123',
            first_name='Test User'
        )
        Profile.objects.create(user=self.user, phone_number='8797456730')

    def test_signup_success(self):
        """Test that submitting signup form creates user and redirects to dashboard"""
        data = {
            'full_name': 'New User',
            'email': 'new@example.com',
            'phone': '9999999999',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        
        response = self.client.post(self.signup_url, data)
            
        self.assertRedirects(response, self.dashboard_url)
        
        # Verify user exists
        self.assertTrue(User.objects.filter(email='new@example.com').exists())
        self.assertTrue(Profile.objects.filter(phone_number='9999999999').exists())
        
        # Verify user is logged in
        user = User.objects.get(email='new@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_password_mismatch(self):
        """Test signup fails when passwords don't match"""
        data = {
            'full_name': 'New User',
            'email': 'fail@example.com',
            'phone': '8888888888',
            'password': 'password123',
            'confirm_password': 'mismatch'
        }
        response = self.client.post(self.signup_url, data)
        
        # Should redirect back to signup
        self.assertRedirects(response, self.signup_url)
        
        # Check for error message
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Passwords do not match!")

    def test_login_success_email(self):
        """Test login with email"""
        data = {
            'identifier': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertRedirects(response, self.dashboard_url)

    def test_login_success_phone(self):
        """Test login with phone number"""
        data = {
            'identifier': '8797456730',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertRedirects(response, self.dashboard_url)

    def test_login_failure(self):
        """Test login with wrong password"""
        data = {
            'identifier': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        
        # Should stay on login page (or re-render it), checking template use here as redirect logic might create loop if not careful
        # Core view renders 'core/login.html' on failure with message
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        
        messages = list(response.context['messages'])
        self.assertEqual(str(messages[0]), "Invalid Email/Phone or Password")
