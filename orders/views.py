from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .services import mark_order_as_paid, OutOfStockError
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from canteen.models import Shift
from menu.models import Inventory, ComboMeal

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        try:
            paid_order = mark_order_as_paid(order)
            serializer = self.get_serializer(paid_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OutOfStockError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class ClientMenuView(LoginRequiredMixin, View):
    """Клієнтське меню — тільки для авторизованих користувачів"""
    def get(self, request):
        current_shift = Shift.objects.filter(status='open').last()
        inventory = []
        combos = []
        if current_shift:
            inventory = Inventory.objects.filter(shift=current_shift).select_related('dish')
            combos = ComboMeal.objects.all() 
        return render(request, 'orders/client_menu.html', {
            'inventory': inventory, 
            'combos': combos,
            'shift': current_shift
        })

class POSView(LoginRequiredMixin, View):
    """POS-термінал — тільки для касирів та адмінів"""
    def get(self, request):
        if request.user.role == 'client':
            return redirect('client_menu')
        current_shift = Shift.objects.filter(status='open').last()
        inventory = []
        if current_shift:
            inventory = Inventory.objects.filter(shift=current_shift).select_related('dish')
        return render(request, 'orders/pos.html', {
            'inventory': inventory,
            'shift': current_shift
        })
