from rest_framework import viewsets, permissions
from django.views.generic import CreateView, RedirectView
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .serializers import UserSerializer
from .forms import CustomUserCreationForm

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        role = self.request.query_params.get('role')
        if role:
            return self.queryset.filter(role=role)
        return self.queryset

class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_signup'] = True
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = 'client'
        user.save()
        
        # Автоматичний вхід після реєстрації
        from django.contrib.auth import login
        login(self.request, user)
        
        return redirect('client_menu')

class RoleBasedRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if user.role == 'admin':
            return reverse('admin_dashboard')
        elif user.role == 'staff':
            return reverse('pos')
        else:
            return reverse('client_menu')
