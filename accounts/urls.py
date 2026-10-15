from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- تسجيل الدخول والخروج ---
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # --- إنشاء حساب جديد وتأكيد الـ OTP ---
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),

    # --- استعادة وإعادة تعيين كلمة السر ---
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),

   
]