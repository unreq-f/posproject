from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['dish', 'combo', 'quantity', 'price_fixed']
        read_only_fields = ['price_fixed']

    def validate(self, data):
        dish = data.get('dish')
        combo = data.get('combo')
        if not dish and not combo:
            raise serializers.ValidationError("Виберіть або страву, або комплекс.")
        if dish and combo:
            raise serializers.ValidationError("Оберіть тільки щось одне: страву або комплекс.")
        return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'shift', 'status', 'order_type', 'payment_method', 'pickup_time', 'total_amount', 'created_at', 'items']
        read_only_fields = ['shift', 'total_amount', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Автоматичний пошук активної зміни
        from canteen.models import Shift
        from menu.models import Inventory
        active_shift = Shift.objects.filter(status='open').last()
        if not active_shift:
            raise serializers.ValidationError("Немає активної зміни. Замовлення неможливе.")
        
        # Перевірка залишків ДО створення замовлення
        for item_data in items_data:
            dish = item_data.get('dish')
            combo = item_data.get('combo')
            qty = item_data['quantity']
            
            if dish:
                inv = Inventory.objects.filter(shift=active_shift, dish=dish).first()
                if not inv or inv.quantity < qty:
                    raise serializers.ValidationError(
                        f"Недостатньо порцій для страви '{dish.name}'. Доступно: {inv.quantity if inv else 0}."
                    )
            elif combo:
                # Перевіряємо кожен компонент комбо
                for combo_dish in combo.dishes.all():
                    inv = Inventory.objects.filter(shift=active_shift, dish=combo_dish).first()
                    if not inv or inv.quantity < qty:
                        raise serializers.ValidationError(
                            f"Недостатньо порцій '{combo_dish.name}' для комплексу '{combo.name}'. Доступно: {inv.quantity if inv else 0}."
                        )
            
        validated_data['shift'] = active_shift
        
        order = Order.objects.create(**validated_data)
        total = 0
        
        for item_data in items_data:
            dish = item_data.get('dish')
            combo = item_data.get('combo')
            price = dish.price if dish else combo.price
            
            OrderItem.objects.create(
                order=order,
                dish=dish,
                combo=combo,
                quantity=item_data['quantity'],
                price_fixed=price
            )
            total += price * item_data['quantity']
            
        order.total_amount = total
        order.save()
        return order
