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
            # Оновлюємо дані про оплату, якщо вони передані (для готівки)
            if 'amount_received' in request.data:
                order.amount_received = request.data.get('amount_received')
            if 'change_amount' in request.data:
                order.change_amount = request.data.get('change_amount')
            if 'payment_method' in request.data:
                order.payment_method = request.data.get('payment_method')
            order.save()

            paid_order = mark_order_as_paid(order)
            serializer = self.get_serializer(paid_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OutOfStockError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Скасування замовлення з поверненням порцій на склад"""
        order = self.get_object()
        if order.status == 'canceled':
            return Response({'detail': 'Замовлення вже скасовано'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.db import transaction
        try:
            with transaction.atomic():
                # Повертаємо товар на склад
                for item in order.items.all():
                    if item.dish:
                        inv, _ = Inventory.objects.get_or_create(shift=order.shift, dish=item.dish)
                        inv.quantity += item.quantity
                        inv.save()
                    elif item.combo:
                        # Для комбо повертаємо всі його компоненти
                        for dish in item.combo.dishes.all():
                            inv, _ = Inventory.objects.get_or_create(shift=order.shift, dish=dish)
                            inv.quantity += item.quantity
                            inv.save()
                
                order.status = 'canceled'
                order.save()
                return Response({'status': 'canceled'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class ClientMenuView(LoginRequiredMixin, View):
    """Меню для клієнтів (онлайн-замовлення)"""
    def get(self, request):
        from canteen.models import Shift
        from datetime import datetime, timedelta
        
        active_shift = Shift.objects.filter(status='open').first()
        inventory = []
        combos = []
        if active_shift:
            inventory = Inventory.objects.filter(shift=active_shift).select_related('dish')
            # Створюємо мапу залишків для швидкої перевірки комбо
            inventory_map = {item.dish_id: item.quantity for item in inventory}
            
            combos_qs = ComboMeal.objects.prefetch_related('dishes').all()
            combos = []
            for combo in combos_qs:
                # Комбо доступне, тільки якщо ВСІ його страви є на вітрині і їх > 0
                combo.is_available = all(inventory_map.get(d.id, 0) > 0 for d in combo.dishes.all())
                combos.append(combo)
        
        # Генерація слотів часу (кожні 15 хв)
        now = datetime.now()
        slots = []
        start_hour = max(now.hour, 8)
        if now.minute > 45:
            start_hour += 1
            start_minute = 0
        else:
            start_minute = ((now.minute // 15) + 1) * 15

        current_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        if now.hour >= 8:
             # If it's already during working hours, start from the next 15-min slot
             minutes_to_add = (15 - now.minute % 15)
             current_time = now + timedelta(minutes=minutes_to_add)

        end_time = now.replace(hour=21, minute=0, second=0, microsecond=0)
        
        temp_time = current_time
        while temp_time < end_time:
            slot_end = temp_time + timedelta(minutes=15)
            slots.append(f"{temp_time.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}")
            temp_time = slot_end

        return render(request, 'orders/client_menu.html', {
            'inventory': inventory,
            'combos': combos,
            'active_shift': active_shift,
            'time_slots': slots[:12] # Показуємо найближчі 3 години
        })

class POSView(LoginRequiredMixin, View):
    """POS-термінал — тільки для касирів та адмінів"""
    def get(self, request):
        if request.user.role not in ['admin', 'staff']:
            return redirect('client_menu')
        
        active_shift = Shift.objects.filter(status='open').first()
        next_order_id = (Order.objects.latest('id').id + 1) if Order.objects.exists() else 1
        online_orders = Order.objects.none()
        
        inventory = []
        if active_shift:
            inventory = Inventory.objects.filter(shift=active_shift).select_related('dish')
            # Онлайн-замовлення, які очікують видачі (і оплачені картою 'paid', і готівкові 'pending')
            online_orders = Order.objects.filter(
                shift=active_shift, 
                order_type='online', 
                status__in=['pending', 'paid']
            ).order_by('pickup_time')
            
        return render(request, 'orders/pos.html', {
            'inventory': inventory,
            'active_shift': active_shift,
            'next_order_id': next_order_id,
            'online_orders': online_orders
        })
