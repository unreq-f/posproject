from rest_framework import serializers
from .models import Shift, WriteOff

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'
        read_only_fields = ['status', 'end_time']

    def validate(self, data):
        # Забороняємо відкривати нову зміну, якщо існує незакрита
        if not self.instance:  # Тільки при створенні (POST)
            open_shift = Shift.objects.filter(status='open').exists()
            if open_shift:
                raise serializers.ValidationError(
                    "Неможливо відкрити нову зміну: попередня зміна ще не закрита."
                )
        return data

class WriteOffSerializer(serializers.ModelSerializer):
    dish_name = serializers.ReadOnlyField(source='dish.name')
    class Meta:
        model = WriteOff
        fields = ['dish_name', 'quantity', 'reason', 'created_at']

from orders.serializers import OrderSerializer
from menu.models import Inventory, Replenishment

class InventorySerializer(serializers.ModelSerializer):
    dish_name = serializers.ReadOnlyField(source='dish.name')
    class Meta:
        model = Inventory
        fields = ['dish_name', 'quantity']

class ReplenishmentSerializer(serializers.ModelSerializer):
    dish_name = serializers.ReadOnlyField(source='dish.name')
    class Meta:
        model = Replenishment
        fields = ['dish_name', 'quantity', 'created_at']

class ShiftDetailSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    inventory = InventorySerializer(many=True, read_only=True)
    write_offs = WriteOffSerializer(many=True, read_only=True, source='writeoffs')
    replenishments = ReplenishmentSerializer(many=True, read_only=True)
    revenue = serializers.SerializerMethodField()
    expected_cash = serializers.SerializerMethodField()
    orders_count = serializers.IntegerField(source='orders.count', read_only=True)

    class Meta:
        model = Shift
        fields = ['id', 'start_time', 'end_time', 'status', 'responsible_staff', 
                  'initial_cash', 'expected_cash', 'orders', 'inventory', 'write_offs', 'replenishments', 'revenue', 'orders_count']

    def get_revenue(self, obj):
        from django.db.models import Sum
        return obj.orders.filter(status__in=['paid', 'completed']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    def get_expected_cash(self, obj):
        from django.db.models import Sum
        cash_total = obj.orders.filter(status__in=['paid', 'completed'], payment_method='cash').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        return obj.initial_cash + cash_total
