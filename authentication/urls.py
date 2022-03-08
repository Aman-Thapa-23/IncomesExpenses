from unicodedata import name
from django.urls import path
from .views import RegistrationView, UsernameValidationView, EmailValidationView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('username-validate', csrf_exempt(UsernameValidationView.as_view()), name='username-validate'),
    path('email-validate', csrf_exempt(EmailValidationView.as_view()), name='email-validate'),
]