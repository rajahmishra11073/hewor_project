from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'), # New URL
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-order/', views.create_order, name='create_order'),
    path('profile/', views.profile_view, name='profile'),
    path('payment/<int:order_id>/', views.payment_view, name='payment'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('faqs/', views.faqs_view, name='faqs'),
    path('case-studies/', views.case_studies_view, name='case_studies'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('contact/', views.contact_view, name='contact'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('order/<int:order_id>/download/<str:file_type>/', views.download_order_files, name='download_order_files'),
    path('order-panel/login/', views.order_panel_login, name='order_panel_login'),
    path('order-panel/', views.order_panel_dashboard, name='order_panel_dashboard'),
    path('order-panel/upload/<int:order_id>/', views.order_panel_upload, name='order_panel_upload'),
    path('order-panel/mark-delivered/<int:order_id>/', views.order_panel_mark_delivered, name='order_panel_mark_delivered'),
    path('order-panel/assign-freelancer/<int:order_id>/', views.order_panel_assign_freelancer, name='order_panel_assign_freelancer'),
    path('order-panel/freelancers/', views.order_panel_freelancers, name='order_panel_freelancers'),
    path('order-panel/manage-works/', views.manage_freelancer_works, name='manage_freelancer_works'),
    path('order-panel/pay-freelancer/<int:order_id>/', views.order_panel_pay_freelancer, name='order_panel_pay_freelancer'),
    path('order-panel/freelancers/delete/<int:freelancer_id>/', views.order_panel_delete_freelancer, name='order_panel_delete_freelancer'),
    path('order-panel/freelancer/<int:freelancer_id>/', views.order_panel_freelancer_detail, name='order_panel_freelancer_detail'),
    path('order-panel/chat/<int:order_id>/', views.order_panel_freelancer_chat, name='order_panel_freelancer_chat'),
    
    # Freelancer Portal
    path('freelancer/login/', views.freelancer_login, name='freelancer_login'),
    path('freelancer/dashboard/', views.freelancer_dashboard, name='freelancer_dashboard'),
    path('freelancer/project/<int:order_id>/', views.freelancer_order_detail, name='freelancer_order_detail'),
    path('freelancer/order/<int:order_id>/accept/', views.freelancer_accept_order, name='freelancer_accept_order'),
    path('freelancer/order/<int:order_id>/reject/', views.freelancer_reject_order, name='freelancer_reject_order'),
]


