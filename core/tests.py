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

    def test_signup_otp_generation(self):
        """Test that submitting signup form generates OTP and redirects"""
        data = {
            'full_name': 'New User',
            'email': 'new@example.com',
            'phone': '9999999999',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        
        # Mock random.randint so we know the OTP
        with patch('core.views.random.randint', return_value=1234):
            response = self.client.post(self.signup_url, data)
            
        self.assertRedirects(response, self.verify_otp_url)
        
        # Verify session data
        session = self.client.session
        self.assertIn('signup_data', session)
        self.assertEqual(session['signup_data']['otp'], 1234)
        self.assertEqual(session['signup_data']['email'], 'new@example.com')

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

    def test_verify_otp_success(self):
        """Test that correct OTP creates user and logs them in"""
        # Manually set session data as if signup occurred
        s = self.client.session
        s['signup_data'] = {
            'full_name': 'Verified User',
            'email': 'verified@example.com',
            'phone': '7777777777',
            'password': 'password123',
            'otp': 5555
        }
        s.save()
        
        response = self.client.post(self.verify_otp_url, {'otp': '5555'})
        
        # Should create user and redirect to dashboard
        self.assertRedirects(response, self.dashboard_url)
        
        # Verify user exists
        new_user = User.objects.get(email='verified@example.com')
        self.assertTrue(Profile.objects.filter(phone_number='7777777777').exists())
        
        # Verify user is logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), new_user.pk)

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
