from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Shift, WriteOff
from .serializers import ShiftSerializer, WriteOffSerializer
from .services import close_shift

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .serializers import ShiftSerializer, WriteOffSerializer, ShiftDetailSerializer

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer

    @action(detail=True, methods=['get'])
    def detailed(self, request, pk=None):
        shift = self.get_object()
        serializer = ShiftDetailSerializer(shift)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        shift = self.get_object()
        try:
            closed_shift = close_shift(shift)
            serializer = self.get_serializer(closed_shift)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WriteOffViewSet(viewsets.ModelViewSet):
    queryset = WriteOff.objects.all()
    serializer_class = WriteOffSerializer

from django.db.models import Sum

class AdminDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'admin':
            return redirect('pos')
        
        from menu.models import Dish, ComboMeal, Inventory
        from orders.models import Order
        
        shifts = Shift.objects.all()
        active_shift = Shift.objects.filter(status='open').first() # ordering is now -id
        dishes = Dish.objects.all()
        combos = ComboMeal.objects.all()
        
        # Загальна аналітика
        total_revenue = Order.objects.filter(status__in=['paid', 'completed']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = Order.objects.count()
        average_check = total_revenue / total_orders if total_orders > 0 else 0
        
        # Дані для нових розділів
        all_orders = Order.objects.all().order_by('-created_at')
        past_shifts = Shift.objects.filter(status='closed').order_by('-end_time')
        
        # Статистика поточної зміни
        current_shift_revenue = 0
        current_shift_orders = 0
        current_shift_inventory = []
        current_shift_orders_list = []
        if active_shift:
            current_shift_revenue = active_shift.orders.filter(status__in=['paid', 'completed']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            current_shift_orders = active_shift.orders.count()
            current_shift_inventory = Inventory.objects.filter(shift=active_shift).select_related('dish')
            current_shift_orders_list = active_shift.orders.all().order_by('-created_at')
            current_shift_cash_total = active_shift.orders.filter(status__in=['paid', 'completed'], payment_method='cash').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            active_shift.expected_cash = active_shift.initial_cash + current_shift_cash_total
        else:
            # Fallback for UI if no active shift but we want to show something?
            pass
        
        return render(request, 'canteen/admin_dashboard.html', {
            'shifts': shifts,
            'active_shift': active_shift,
            'dishes': dishes,
            'combos': combos,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'average_check': average_check,
            'all_orders': all_orders,
            'past_shifts': past_shifts,
            'current_shift_revenue': current_shift_revenue,
            'current_shift_orders': current_shift_orders,
            'current_shift_inventory': current_shift_inventory,
            'current_shift_orders_list': current_shift_orders_list,
        })
