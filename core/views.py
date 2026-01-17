import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceOrder, Profile, SiteSetting, ContactMessage, OrderChat
from django.conf import settings
import random
import logging
# Re-import firebase_admin for Google Auth
import firebase_admin
from firebase_admin import auth as firebase_auth

logger = logging.getLogger(__name__)

# --- HELPER FUNCTIONS ---
def get_user_by_email_or_phone(identifier):
    try:
        user = User.objects.get(email=identifier)
        return user
    except User.DoesNotExist:
        pass
    
    try:
        profile = Profile.objects.get(phone_number=identifier)
        return profile.user
    except Profile.DoesNotExist:
        pass
    return None

def verify_google_token(id_token):
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.error(f"Error verifying Firebase token: {e}")
        return None

def validate_input(email, phone):
    # Regex for Email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Invalid email address format."
    
    # Regex for Phone (Allow +91 or just 10 digits)
    phone_regex = r'^(\+91[\-\s]?)?[0]?(91)?[6789]\d{9}$'
    if not re.match(phone_regex, phone):
        return False, "Invalid phone number. Must be a valid Indian mobile number."
        
    return True, ""

# --- VIEWS ---

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def signup_view(request):
    if request.method == 'POST':
        # Check for Google Sign-In first
        id_token = request.POST.get('google_id_token')
        if id_token:
            decoded_token = verify_google_token(id_token)
            if decoded_token:
                email = decoded_token.get('email')
                name = decoded_token.get('name')
                # Google Users verified by default
                
                # Check if user exists
                user = User.objects.filter(email=email).first()
                if not user:
                    # Create new Google User
                    username = email.split('@')[0] + str(random.randint(1000,9999))
                    user = User.objects.create_user(username=username, email=email)
                    user.first_name = name
                    user.save()
                    Profile.objects.create(user=user) # Empty phone for google initially
                
                login(request, user)
                return redirect('dashboard')
            else:
                 messages.error(request, "Google Sign-In failed.")
                 return redirect('signup')

        # Standard Signup
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 1. Regex Validation
        is_valid, error_msg = validate_input(email, phone)
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('signup')
            
        if Profile.objects.filter(phone_number=phone).exists():
            messages.error(request, "Phone number already registered!")
            return redirect('signup')
        
        # Create User
        try:
            # We use phone number as username to ensure uniqueness
            user = User.objects.create_user(
                username=phone, 
                email=email,
                password=password
            )
            user.first_name = full_name
            user.save()
            
            Profile.objects.create(user=user, phone_number=phone)
            
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return redirect('signup')

    return render(request, 'core/signup.html')

def verify_otp(request):
    # Deprecated view, redirecting to home
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        # Check for Google Sign-In first
        id_token = request.POST.get('google_id_token')
        if id_token:
            decoded_token = verify_google_token(id_token)
            if decoded_token:
                email = decoded_token.get('email')
                
                # Check if user exists
                user = User.objects.filter(email=email).first()
                if user:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    # Optional: Auto-create account on login if it doesn't exist?
                    # For now, let's redirect to signup with a message or just create it.
                    # User requested "Sign in with Google" which usually implies auto-signup.
                    name = decoded_token.get('name')
                    username = email.split('@')[0] + str(random.randint(1000,9999))
                    user = User.objects.create_user(username=username, email=email)
                    user.first_name = name
                    user.save()
                    Profile.objects.create(user=user)
                    login(request, user)
                    return redirect('dashboard')
            else:
                 messages.error(request, "Google Sign-In failed.")
                 return redirect('login')

        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        
        user = get_user_by_email_or_phone(identifier)
        
        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        
        messages.error(request, "Invalid Email/Phone or Password")
    
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    orders = ServiceOrder.objects.filter(user=request.user).order_by('-created_at')
    
    stats = {
        'total': orders.count(),
        'pending': orders.filter(status='pending').count(),
        'in_progress': orders.filter(status='in_progress').count(),
        'completed': orders.filter(status='completed').count(),
    }
    
    return render(request, 'core/dashboard.html', {'orders': orders, 'stats': stats})

@login_required
def create_order(request):
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        phone_number = request.POST.get('phone_number')
        request_call = request.POST.get('request_call') == 'on'
        file = request.FILES.get('file_upload')
        
        ServiceOrder.objects.create(
            user=request.user,
            service_type=service_type,
            title=title,
            description=description,
            phone_number=phone_number,
            request_call=request_call,
            file_upload=file
        )
        messages.success(request, "Order received successfully!")
        return redirect('dashboard')
        
    return render(request, 'core/create_order.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        if request.POST.get('full_name'):
            user.first_name = request.POST.get('full_name')
        if request.POST.get('email'):
            user.email = request.POST.get('email')
        user.save()

        profile, created = Profile.objects.get_or_create(user=user)
        profile.phone_number = request.POST.get('phone')
        
        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES.get('profile_image')
        
        profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'core/profile.html')

@login_required
def payment_view(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id, user=request.user)
    
    if request.method == 'POST':
        if request.FILES.get('payment_screenshot'):
            order.payment_screenshot = request.FILES.get('payment_screenshot')
            order.transaction_id = request.POST.get('transaction_id')
            order.is_paid = True
            order.save()
            
            messages.success(request, "Payment proof uploaded! We will verify shortly.")
            return redirect('dashboard')
            
    return render(request, 'core/payment.html', {'order': order})

# --- DYNAMIC PAGES LOGIC ---

def about_view(request):
    setting = SiteSetting.objects.first()
    return render(request, 'core/about.html', {'setting': setting})

def contact_view(request):
    setting = SiteSetting.objects.first()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message
        )
        messages.success(request, "Message sent! We will contact you soon.")
        return redirect('contact')
        
    return render(request, 'core/contact.html', {'setting': setting})

def services_view(request):
    return render(request, 'core/services.html')

def faqs_view(request):
    return render(request, 'core/faqs.html')

def case_studies_view(request):
    return render(request, 'core/case_studies.html')

def terms_view(request):
    return render(request, 'core/terms.html')

# --- NEW ORDER DETAIL & CHAT VIEW (UPDATED) ---
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id)
    
    # Security Check: Sirf apna order ya Admin dekh sake
    if request.user != order.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to view this order.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        message = request.POST.get('message')
        
        if message:
            # Chat message create karo
            OrderChat.objects.create(
                order=order,
                sender=request.user,
                message=message
            )
            
            # Optional: Agar Admin reply kare toh status update ho
            if request.user.is_superuser:
                # Agar status pending hai to In Progress kar do
                if order.status == 'pending':
                    order.status = 'in_progress'
                    order.save()
            
            # Redirect to same page to avoid re-submission
            return redirect('order_detail', order_id=order.id)

    # Purani chats fetch karo (oldest first)
    chats = order.chats.all().order_by('created_at')
    
    return render(request, 'core/order_detail.html', {'order': order, 'chats': chats})

# --- CHATBOT API ---
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .chatbot_logic import get_chatbot_response

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Artificial Delay for realism (Optional, removed for speed)
            response_text = get_chatbot_response(request.user, message)
            
            return JsonResponse({'response': response_text, 'status': 'success'})
        except Exception as e:
            return JsonResponse({'response': "Error processing request.", 'status': 'error'})
    return JsonResponse({'status': 'invalid_method'})