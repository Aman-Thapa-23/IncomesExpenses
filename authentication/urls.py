from unicodedata import name
from django.urls import path
from .views import RegistrationView, LoginView, LogoutView ,UsernameValidationView, EmailValidationView, VerificationView
from django.views.decorators.csrf import csrf_exempt

app_name='authenticate'

urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout',LogoutView.as_view(), name='logout'),
    path('username-validate', csrf_exempt(UsernameValidationView.as_view()), name='username-validate'),
    path('email-validate', csrf_exempt(EmailValidationView.as_view()), name='email-validate'),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name='activate'),
]