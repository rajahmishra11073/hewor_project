import re
from django.shortcuts import render, redirect, get_object_or_404
import zipfile
import io
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceOrder, OrderFile, Profile, SiteSetting, ContactMessage, OrderChat, Review, CaseStudy, AgencyStat, TeamMember, Freelancer, FreelancerChat
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
import datetime
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
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'core/home.html', {'reviews': reviews})

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
        files = request.FILES.getlist('file_upload')
        
        
        # Check for existing order with same title
        order = ServiceOrder.objects.filter(user=request.user, title=title).first()
        
        is_new_order = False
        if not order:
            # Create new order if not exists
            order = ServiceOrder.objects.create(
                user=request.user,
                service_type=service_type,
                title=title,
                description=description,
                phone_number=phone_number,
                request_call=request_call,
            )
            is_new_order = True
        else:
             # Logic for Merged Order (Optional: Update description? For now, keep original to avoid overwrite)
             pass

        from .models import OrderFile
        files_added = 0
        
        for f in files:
            # Check for duplicate file name in this order
            if not OrderFile.objects.filter(order=order, original_filename=f.name).exists():
                 OrderFile.objects.create(order=order, file=f, file_type='source', original_filename=f.name)
                 files_added += 1

        if is_new_order:
            messages.success(request, "Order received successfully!")
        elif files_added > 0:
            messages.success(request, f"New files added to existing project: '{title}'")
        else:
             messages.info(request, f"Project '{title}' already exists and no new files were added.")
             
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
    team_members = TeamMember.objects.all().order_by('order')
    return render(request, 'core/about.html', {
        'setting': setting,
        'team_members': team_members
    })

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
    case_studies = CaseStudy.objects.all().order_by('order')
    stats = AgencyStat.objects.all().order_by('order')
    setting = SiteSetting.objects.first()
    return render(request, 'core/case_studies.html', {
        'case_studies': case_studies,
        'agency_stats': stats,
        'setting': setting
    })

def terms_view(request):
    return render(request, 'core/terms.html')

def privacy(request):
    """Render the privacy policy page."""
    return render(request, 'core/privacy.html')

# --- NEW ORDER DETAIL & CHAT VIEW (UPDATED) ---
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id)
    
    # Security Check: Sirf apna order ya Admin dekh sake
    if request.user != order.user and not request.user.is_superuser and request.user.username != 'Hewor.order':
        messages.error(request, "You are not authorized to view this order.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        # File Upload Logic
        if 'file_upload' in request.FILES:
            files = request.FILES.getlist('file_upload')
            upload_type = request.POST.get('upload_type', 'source')
            
            # Security: Non-admin users can ONLY upload source files
            if not request.user.is_superuser:
                upload_type = 'source'
            
            from .models import OrderFile
            for f in files:
                # Deduplication for additional uploads
                if not OrderFile.objects.filter(order=order, original_filename=f.name).exists():
                    OrderFile.objects.create(order=order, file=f, file_type=upload_type, original_filename=f.name)
            
            messages.success(request, f"{upload_type.title()} files uploaded successfully.")
            
            # Auto-update status if Admin delivers work
            if request.user.is_superuser and upload_type == 'delivery':
                if order.status != 'completed':
                    order.status = 'completed'
                    from django.utils import timezone
                    order.completed_at = timezone.now()
                    order.save()
            return redirect('order_detail', order_id=order.id)

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
    
    # Separation of files
    source_files = order.files.filter(file_type='source')
    delivery_files = order.files.filter(file_type='delivery')
    
    return render(request, 'core/order_detail.html', {
        'order': order, 
        'chats': chats,
        'source_files': source_files,
        'delivery_files': delivery_files
    })

@login_required
def download_order_files(request, order_id, file_type):
    order = get_object_or_404(ServiceOrder, id=order_id)
    
    if request.user != order.user and not request.user.is_superuser:
        messages.error(request, "Access denied.")
        return redirect('dashboard')
    
    files = order.files.filter(file_type=file_type)
    
    if not files.exists():
        messages.error(request, "No files found.")
        return redirect('order_detail', order_id=order.id)
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for f in files:
            try:
                file_path = f.file.path
                file_name = f.file.name.split('/')[-1]
                zip_file.write(file_path, file_name)
            except FileNotFoundError:
                continue # Skip missing files
    
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{file_type}_files_{order.id}.zip"'
    return response

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

# --- ORDER PANEL VIEWS ---
def order_panel_login(request):
    if request.user.is_authenticated:
        return redirect('order_panel_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('order_panel_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/order_panel_login.html', {'form': form})

@login_required(login_url='order_panel_login')
def order_panel_dashboard(request):
    orders = ServiceOrder.objects.all().order_by('-created_at')
    freelancers = Freelancer.objects.all().order_by('name')
    return render(request, 'core/order_panel_dashboard.html', {'orders': orders, 'freelancers': freelancers})

@login_required(login_url='order_panel_login')
def order_panel_upload(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(ServiceOrder, pk=order_id)
        files = request.FILES.getlist('file_upload')
        file_type = request.POST.get('file_type', 'delivery')
        
        for f in files:
            if not OrderFile.objects.filter(order=order, original_filename=f.name).exists():
                OrderFile.objects.create(
                    order=order, 
                    file=f, 
                    file_type=file_type, 
                    original_filename=f.name
                )
        messages.success(request, f"{len(files)} files uploaded.")
    return redirect('order_panel_dashboard')

@login_required(login_url='order_panel_login')
def order_panel_mark_delivered(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(ServiceOrder, pk=order_id)
        order.status = 'completed'
        from django.utils import timezone
        order.completed_at = timezone.now()
        order.save()
        messages.success(request, f"Order #{order.id} marked as Delivered.")
    return redirect('order_panel_dashboard')


@login_required(login_url='order_panel_login')
def order_panel_freelancers(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        freelancer_id = request.POST.get('freelancer_id')
        phone = request.POST.get('phone')
        profession = request.POST.get('profession')
        address = request.POST.get('address')
        expertise = request.POST.get('expertise')
        profile_pic = request.FILES.get('profile_pic')
        password = request.POST.get('password') # Pass this from form
        
        qr_code = request.FILES.get('qr_code')
        payment_details = request.POST.get('payment_details')

        if Freelancer.objects.filter(freelancer_id=freelancer_id).exists():
            messages.error(request, f"Freelancer ID {freelancer_id} already exists.")
        else:
            try:
                # 1. Create User for Login
                user = User.objects.create_user(username=freelancer_id, password=password)
                
                # 2. Create Freelancer linked to User
                Freelancer.objects.create(
                    user=user,
                    name=name, freelancer_id=freelancer_id, phone=phone,
                    profession=profession, address=address, expertise=expertise,
                    profile_pic=profile_pic,
                    qr_code=qr_code, payment_details=payment_details
                )
                messages.success(request, f"Freelancer {name} added with Login ID: {freelancer_id}")
            except Exception as e:
                messages.error(request, f"Error creating freelancer: {str(e)}")
                
        return redirect('order_panel_freelancers')

    freelancers = Freelancer.objects.all().order_by('-joined_at')
    return render(request, 'core/order_panel_freelancers.html', {'freelancers': freelancers, 'active_tab': 'profiles'})

@login_required(login_url='order_panel_login')
def order_panel_freelancer_detail(request, freelancer_id):
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    assigned_orders = ServiceOrder.objects.filter(freelancer=freelancer).order_by('-assigned_at')
    
    context = {
        'freelancer': freelancer,
        'assigned_orders': assigned_orders,
        'active_count': assigned_orders.filter(status='in_progress').count(),
        'completed_count': assigned_orders.filter(status='completed').count(),
        'pending_acceptance_count': assigned_orders.filter(freelancer_status='pending_acceptance').count(),
    }
    return render(request, 'core/admin/freelancer_details.html', context)

@login_required(login_url='order_panel_login')
def order_panel_assign_freelancer(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(ServiceOrder, pk=order_id)
        freelancer_id = request.POST.get('freelancer_id')
        roadmap = request.FILES.get('freelancer_roadmap')
        description = request.POST.get('freelancer_description')

        if freelancer_id:
            freelancer = get_object_or_404(Freelancer, id=freelancer_id)
            order.freelancer = freelancer
            
            if roadmap:
                order.freelancer_roadmap = roadmap
            if description:
                order.freelancer_description = description
            
            # Set Assignment Details
            order.assigned_at = timezone.now()
            order.freelancer_status = 'pending_acceptance'
            # Default deadline (e.g., 2 days from now, can be made dynamic later)
            order.freelancer_deadline = timezone.now() + datetime.timedelta(days=2)
            
            order.save()
            
            # --- NOTIFICATION LOGIC ---
            # 1. Email Notification
            subject = f"New Work Assigned: {order.title}"
            message = f"""
            Hello {freelancer.name},
            
            You have been assigned a new project: "{order.title}".
            
            Price: Discussed with Admin.
            Description: {description or 'Check dashboard for details.'}
            
            Please login to your dashboard to Accept or Reject this order within 30 minutes.
            
            Login Here: {request.build_absolute_uri('/freelancer/login/')}
            """
            try:
                if freelancer.user.email:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [freelancer.user.email])
            except Exception as e:
                print(f"Email sending failed: {e}")
                
            # 2. WhatsApp Notification (Placeholder)
            print(f"--- WHATSAPP NOTIFICATION ---")
            print(f"To: {freelancer.phone}")
            print(f"Msg: New Order Assigned: {order.title}. Accept in 30 mins.")
            print(f"-----------------------------")
            
            messages.success(request, f"Order assigned to {freelancer.name}. Notifications sent.")
            
    return redirect('order_panel_dashboard')

@login_required(login_url='order_panel_login')
def order_panel_delete_freelancer(request, freelancer_id):
    if request.method == 'POST':
        freelancer = get_object_or_404(Freelancer, id=freelancer_id)
        freelancer.delete()
        messages.success(request, "Freelancer deleted successfully.")
    return redirect('order_panel_freelancers')

# --- 4b. FREELANCER ORDER CHAT ---
@login_required(login_url='order_panel_login')
def order_panel_freelancer_chat(request, order_id):
    # This view is for ADMIN side to chat with freelancer
    order = get_object_or_404(ServiceOrder, id=order_id)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        attachment = request.FILES.get('attachment')
        if message or attachment:
            FreelancerChat.objects.create(
                order=order,
                sender=request.user,
                message=message,
                attachment=attachment
            )
            return redirect('order_panel_freelancer_chat', order_id=order.id)
            
    chats = order.freelancer_chats.all().order_by('created_at')
    return render(request, 'core/order_panel_chat.html', {'order': order, 'chats': chats})

# --- FREELANCER PORTAL VIEWS ---

def freelancer_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'freelancer'):
        return redirect('freelancer_dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Ensure it's a freelancer account
            if hasattr(user, 'freelancer'):
                login(request, user)
                return redirect('freelancer_dashboard')
            else:
                messages.error(request, "Not a freelancer account.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/freelancer_login.html', {'form': form})

@login_required(login_url='freelancer_login')
def freelancer_dashboard(request):
    try:
        freelancer = request.user.freelancer
    except Freelancer.DoesNotExist:
        logout(request)
        return redirect('freelancer_login')
        
    # --- AUTO-TIMEOUT LOGIC ---
    # Check for pending orders that have exceeded 30 minutes
    timeout_threshold = timezone.now() - datetime.timedelta(minutes=30)
    expired_orders = ServiceOrder.objects.filter(
        freelancer=freelancer,
        freelancer_status='pending_acceptance',
        assigned_at__lt=timeout_threshold
    )
    # Update them to 'timeout'
    if expired_orders.exists():
        count = expired_orders.update(freelancer_status='timeout')
        print(f"Auto-timed out {count} orders for {freelancer.name}")

    orders = ServiceOrder.objects.filter(freelancer=freelancer).order_by('-created_at')
    return render(request, 'core/freelancer_dashboard.html', {'orders': orders})

@login_required(login_url='order_panel_login')
def order_panel_pay_freelancer(request, order_id):
    order = get_object_or_404(ServiceOrder, pk=order_id)
    if request.method == 'POST':
        try:
            transaction_id = request.POST.get('transaction_id')
            screenshot = request.FILES.get('payment_screenshot')
            
            if transaction_id:
                order.is_freelancer_paid = True
                order.freelancer_transaction_id = transaction_id
                if screenshot:
                    order.freelancer_payment_screenshot = screenshot
                order.save()
                messages.success(request, f"Payment recorded for Freelancer: {order.freelancer.name}")
            else:
                messages.error(request, "Transaction ID is required.")
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            
    return redirect('manage_freelancer_works')

# Redoing the tool call with the actual code after I update the model. 
# actually, I should update the model FIRST.
# Cancelling this replacement to update model first.


@login_required(login_url='order_panel_login')
def manage_freelancer_works(request):
    # Fetch all orders that have been assigned to a freelancer
    assignments = ServiceOrder.objects.filter(freelancer__isnull=False).order_by('-assigned_at')
    
    context = {
        'assignments': assignments,
        'active_tab': 'works'
    }
    return render(request, 'core/manage_freelancer_works.html', context)


@login_required(login_url='freelancer_login')
def freelancer_order_detail(request, order_id):
    try:
        freelancer = request.user.freelancer
    except Freelancer.DoesNotExist:
        logout(request)
        return redirect('freelancer_login')
        
    order = get_object_or_404(ServiceOrder, id=order_id, freelancer=freelancer)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'upload_work':
            files = request.FILES.getlist('files')
            if files:
                for f in files:
                    OrderFile.objects.create(
                        order=order,
                        file=f,
                        file_type='freelancer_upload',
                        original_filename=f.name
                    )
                messages.success(request, f"{len(files)} files uploaded successfully.")
                
        elif action == 'send_message':
            message = request.POST.get('message')
            attachment = request.FILES.get('attachment')
            if message or attachment:
                FreelancerChat.objects.create(
                    order=order,
                    sender=request.user,
                    message=message,
                    attachment=attachment
                )
        return redirect('freelancer_order_detail', order_id=order.id)
            
    chats = order.freelancer_chats.all().order_by('created_at')
    uploaded_files = order.files.filter(file_type='freelancer_upload').order_by('-uploaded_at')
    
    return render(request, 'core/freelancer_order_detail.html', {
        'order': order,
        'chats': chats,
        'uploaded_files': uploaded_files
    })

@login_required(login_url='freelancer_login')
def freelancer_accept_order(request, order_id):
    try:
        freelancer = request.user.freelancer
    except Freelancer.DoesNotExist:
        return redirect('freelancer_login')
        
    order = get_object_or_404(ServiceOrder, id=order_id, freelancer=freelancer)
    
    if order.freelancer_status != 'pending_acceptance':
        messages.error(request, "Order is not pending acceptance.")
        return redirect('freelancer_dashboard')
        
    # Check 30 minute timeout
    time_diff = timezone.now() - order.assigned_at
    if time_diff.total_seconds() > 1800: # 30 minutes * 60 seconds
        order.freelancer_status = 'timeout'
        order.save()
        messages.error(request, "Order acceptance time expired.")
    else:
        order.freelancer_status = 'accepted'
        order.save()
        messages.success(request, "Order accepted successfully!")
        
    return redirect('freelancer_dashboard')

@login_required(login_url='freelancer_login')
def freelancer_reject_order(request, order_id):
    try:
        freelancer = request.user.freelancer
    except Freelancer.DoesNotExist:
        return redirect('freelancer_login')
        
    order = get_object_or_404(ServiceOrder, id=order_id, freelancer=freelancer)
    
    if order.freelancer_status == 'pending_acceptance':
        order.freelancer_status = 'rejected'
        order.save()
        messages.info(request, "Order rejected.")
        
    return redirect('freelancer_dashboard')
