from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['price_fixed']

    def create(self, validated_data):
        # Автоматически проставляем цену из связанного блюда или комбо
        dish = validated_data.get('dish')
        combo = validated_data.get('combo')
        
        if dish:
            validated_data['price_fixed'] = dish.price
        elif combo:
            validated_data['price_fixed'] = combo.price
        else:
            validated_data['price_fixed'] = 0.00
            
        return super().create(validated_data)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['total_amount', 'created_at']
