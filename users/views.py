from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

class RoleBasedRedirectView(LoginRequiredMixin, View):
    """Редирект після логіну залежно від ролі користувача"""
    def get(self, request):
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'cashier':
            return redirect('pos')
        else:
            return redirect('client_menu')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SignupView(View):
    """Реєстрація нового клієнта"""
    def post(self, request):
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()

        errors = []
        if not username or not password:
            errors.append('Заповніть всі обов\'язкові поля.')
        if password != password2:
            errors.append('Паролі не співпадають.')
        if len(password) < 6:
            errors.append('Пароль має бути не менше 6 символів.')
        if User.objects.filter(username=username).exists():
            errors.append('Користувач з таким логіном вже існує.')

        if errors:
            return render(request, 'users/login.html', {
                'signup_errors': errors,
                'show_signup': True,
                'signup_username': username,
                'signup_first_name': first_name,
            })

        user = User(username=username, first_name=first_name, role='client')
        user.set_password(password)
        user.save()

        login(request, user)
        return redirect('client_menu')

