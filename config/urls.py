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

from users.views import UserViewSet
from canteen.views import ShiftViewSet, WriteOffViewSet
from menu.views import DishViewSet, ComboMealViewSet, MenuViewSet, InventoryViewSet
from orders.views import OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'shifts', ShiftViewSet)
router.register(r'writeoffs', WriteOffViewSet)
router.register(r'dishes', DishViewSet)
router.register(r'combos', ComboMealViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
