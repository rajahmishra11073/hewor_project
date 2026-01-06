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
    path('contact/', views.contact_view, name='contact'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
]


