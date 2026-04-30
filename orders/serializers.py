from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = OrderItem
        fields = ['dish', 'combo', 'item_name', 'quantity', 'price_fixed']
        read_only_fields = ['price_fixed', 'item_name']

    def get_item_name(self, obj):
        if obj.dish: return obj.dish.name
        if obj.combo: return obj.combo.name
        return "Невідомий товар"

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
    amount_received = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, default=0)
    
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'client', 'shift', 'status', 'order_type', 'order_type_display', 'payment_method', 'pickup_time', 'total_amount', 'amount_received', 'change_amount', 'created_at', 'items']
        read_only_fields = ['shift', 'total_amount', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Автоматичний пошук активної зміни
        from canteen.models import Shift
        from .services import deduct_inventory_from_order, OutOfStockError
        from django.db import transaction
        
        active_shift = Shift.objects.filter(status='open').first()
        if not active_shift:
            raise serializers.ValidationError("Немає активної зміни. Замовлення неможливе.")
        
        validated_data['shift'] = active_shift
        
        try:
            with transaction.atomic():
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
                
                # РЕЗЕРВУВАННЯ (Списання з вітрини)
                deduct_inventory_from_order(order)
                
                return order
        except OutOfStockError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            raise serializers.ValidationError(f"Помилка створення замовлення: {str(e)}")
