
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


from .utils import accout_activation_token
from validate_email import validate_email
import json
# Create your views here.


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

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('authenticate:activate', kwargs={
                               'uidb64': uidb64, 'token': accout_activation_token.make_token(user)})
                activate_url = 'http://'+domain+link

                email_subject = "Activate your account"
                email_body = f"Hi, {user.username}. Please click this link to verify your account\n" + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'hahah@gmail.com',
                    [email],
                )

                email.send(fail_silently=True)
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