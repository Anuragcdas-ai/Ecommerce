from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        login_url = reverse('accounts:login')
        logout_url = reverse('accounts:logout')
        register_url= reverse('accounts:register')
        register_merchant_url = reverse('accounts:become_merchant')

        exempt_urls = [
            login_url,
            logout_url,
            register_url,
            register_merchant_url,
         
        ]

        is_exempt = request.path.startswith(tuple(exempt_urls))
        is_admin = request.path.startswith('/admin/')

        if not request.user.is_authenticated and not (is_exempt or is_admin):
            return redirect(login_url)

        response = self.get_response(request)

        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response