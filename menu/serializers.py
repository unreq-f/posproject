from rest_framework import serializers
from .models import Dish, ComboMeal, Inventory

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'

class ComboMealSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComboMeal
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

class AddInventorySerializer(serializers.Serializer):
    dish_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
