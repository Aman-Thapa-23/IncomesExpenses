
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login, logout

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.auth.tokens import PasswordResetTokenGenerator

import threading

from .utils import accout_activation_token
from validate_email import validate_email
import json
# Create your views here.


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=False)

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric character'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username is already taken. Please choose anther one'}, status=409)

        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email is already in use. Please use another one'}, status=409)

        return JsonResponse({'email_valid': True})


class RegistrationView(View):

    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldvalues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password is too short")
                    return render(request, 'authentication/register.html', context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                # path_to_view to verify the user
                # - getting domain we are on
                # - relative url to verification
                # - encode uid
                # - token
                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain, 
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': accout_activation_token.make_token(user)
                }
                link = reverse('authenticate:activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                activate_url = 'http://'+current_site.domain+link

                email_subject = "Activate your account"
                email_body = f"Hi, {user.username}. Please click this link to verify your account\n" + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@gmail.com',
                    [email],
                )

                EmailThread(email).start()
                messages.success(request, "Account successfully created")
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not accout_activation_token.check_token(user, token):
                return redirect('authenticate:login' + '?message= User is already activated.')

            if user.is_active:
                return redirect('authenticate:login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully.')
            return redirect('authenticate:login')

        except Exception as ex:
            pass

        return redirect('authenticate:login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"welcome {user.username}, you are now logged in.")
                    return redirect('expense:expenses')

                messages.error(request, "Account is not active. please check your email.")
                return render(request, 'authentication/login.html')

            messages.error(request, "Invalid credentials. Try again.")
            return render(request, 'authentication/login.html')
        
        messages.error(request, "Please fill up the fields.")
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('authenticate:login')


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset_password.html')

    def post(self, request):
        email = request.POST['email']

        context = {
            'values': request.POST
        }

        if not validate_email(email=email):
            messages.error(request, "Please enter a valid email")
            return render(request, 'authentication/reset_password.html', context)
        
        current_site = get_current_site(request)
        user = User.objects.filter(email=email)
        if user.exists():
            email_contents = {
                'user': user[0], # to get first user to verify
                'domain': current_site.domain, 
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0])
            }
            link = reverse('authentication:reset-new-password', kwargs={'uidb64': email_contents['uid'], 'token': email_contents['token']})
            reset_url = 'http://'+current_site.domain+link
            email_subject = "Password Reset Instructions"
            email_body = f"Hi there, please click this link to reset your password\n" + reset_url
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@gmail.com',
                [email],               
                )
            EmailThread(email).start()
        messages.success(request, 'We have sent you an email to reset your password.')
        
        return render(request, 'authentication/reset_password.html')


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Link is already expired. Please request a new one.')
                return render(request, 'authentication/set_newpassword.html', context)
        except Exception as identifier:
            messages.info(request, 'Something went wrong, try again.')

        return render(request, 'authentication/set_newpassword.html', context)

    def post(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST['password']
        password1 = request.POST['password1']

        if password != password1:
            messages.error(request, 'Password do not match.') 
            return render(request, 'authentication/set_newpassword.html', context)

        if len(password) < 8:
            messages.error(request, 'Password is too short.')
            return render(request, 'authentication/set_newpassword.html', context)


        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully. Now, you can use new password to login.')
            return redirect('authentication:login')
        except Exception as identifier:
            messages.info(request, 'Something went wrong, try again.')
        
        return render(request, 'authentication/set_newpassword.html', context)