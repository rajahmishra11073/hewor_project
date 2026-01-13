from django.db import models
from django.contrib.auth.models import User

# --- 1. PROFILE MODEL ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', default='default.jpg', blank=True, null=True)
    
    def __str__(self):
        return self.user.username

# --- 2. SERVICE ORDER MODEL ---
class ServiceOrder(models.Model):
    SERVICE_CHOICES = [
        ('presentation', 'Presentation / PPT Creation'),
        ('book_typing', 'Book Typing / Structured Data'),
        ('consultation', 'One-to-One Consultation Call'),
        ('web_scraping', 'Web Scraping'),
        ('data_entry', 'Data Entry'),
        ('other', 'Other Custom Requirement'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('contacted', 'Client Contacted'),
        ('in_progress', 'Work in Progress'),
        ('completed', 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Describe your project in detail.")
    file_upload = models.FileField(upload_to='uploads/', blank=True, null=True)
    
    # Contact Info
    request_call = models.BooleanField(default=False, verbose_name="Request a Callback")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # Payment Fields
    is_paid = models.BooleanField(default=False)
    payment_screenshot = models.ImageField(upload_to='payments/', blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    # Delivery Fields
    delivery_file = models.FileField(upload_to='deliveries/', blank=True, null=True, help_text="Upload the final project file here.")
    delivery_message = models.TextField(blank=True, null=True, help_text="Message to the client upon delivery.")
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

# --- 3. DYNAMIC PAGES SETTINGS ---
class SiteSetting(models.Model):
    about_title = models.CharField(max_length=200, default="About Hewor")
    about_description = models.TextField(help_text="Write your company story here.")
    about_image = models.ImageField(upload_to='site/', blank=True, null=True)
    
    contact_email = models.EmailField(default="support@hewor.com")
    contact_phone = models.CharField(max_length=20, default="+91 8797456730")
    contact_address = models.TextField(default="Tech Park, New Delhi, India")
    
    def __str__(self):
        return "Site Configuration (Edit this)"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.name}"

# --- 4. ORDER CHAT MODEL (Ye Missing tha) ---
class OrderChat(models.Model):
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name='chats')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat on {self.order.title} by {self.sender.username}"