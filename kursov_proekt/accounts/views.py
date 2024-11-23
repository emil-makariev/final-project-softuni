from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.urls import reverse

from kursov_proekt.accounts.forms import BaseUserForm, LoginForm
from kursov_proekt.settings import EMAIL_HOST_USER


# Create your views here.

class CreateUserView(CreateView):
    template_name = 'user/register.html'
    success_url = reverse_lazy('common')
    model = get_user_model()
    form_class = BaseUserForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Ensure the user is inactive initially
        user.save()

        # Generate token and UID for email verification
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        # Create email content using the activation_email.html template
        subject = 'Activate Your Account'
        message = render_to_string(
            'user/activation_email.html',
            {
                'user': user,
                'uid': uid,
                'token': token,
                'protocol': 'http',  # You can change this to 'https' if using HTTPS
                'domain': get_current_site(self.request).domain,  # Ensure this is just the domain
            }
        )

        # Send the email with the correct content type for HTML
        send_mail(
            subject,
            message,  # This is the plain text version (optional if using html_message)
            EMAIL_HOST_USER,
            [user.email],  # The user's email address
            fail_silently=False,
            html_message=message  # Specify the HTML content here
        )

        return redirect('email-message')  # Redirect after successful registration


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
        print(user)
        print(token)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        user.backend = 'kursov_proekt.accounts.authentication_backend.EmailOrUsernameBackend'

        login(request, user)

        return redirect('email-message')

    else:
        return HttpResponse('Activation link is invalid or expired', status=400)


def email_message(request):
    return render(request, context=None, template_name='user/activation-page.html')


class LoginViewCustom(LoginView):
    template_name = 'user/log-in.html'
    form_class = LoginForm
    success_url = reverse_lazy('common')
