from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'order_type', 'payment_method', 'total_amount', 'created_at')
    list_filter = ('status', 'order_type', 'payment_method', 'shift')
    inlines = [OrderItemInline]
