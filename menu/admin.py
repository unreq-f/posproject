from django.contrib import admin
from .models import Dish, ComboMeal, Inventory

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(ComboMeal)
class ComboMealAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('shift', 'dish', 'quantity')
    list_filter = ('shift', 'dish')
