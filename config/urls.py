"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.contrib.auth import views as auth_views
from users.views import UserViewSet, SignupView, RoleBasedRedirectView
from canteen.views import ShiftViewSet, WriteOffViewSet, AdminDashboardView
from menu.views import DishViewSet, ComboMealViewSet, InventoryViewSet
from orders.views import OrderViewSet, OrderItemViewSet, POSView, ClientMenuView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'shifts', ShiftViewSet)
router.register(r'writeoffs', WriteOffViewSet)
router.register(r'dishes', DishViewSet)
router.register(r'combos', ComboMealViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RoleBasedRedirectView.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # Frontend Template Views
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('redirect/', RoleBasedRedirectView.as_view(), name='role_redirect'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('pos/', POSView.as_view(), name='pos'),
    path('client/', ClientMenuView.as_view(), name='client_menu'),
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
