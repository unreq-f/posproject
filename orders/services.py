from django.db import transaction
from django.db.models import F
from .models import Order
from menu.models import Inventory

class OutOfStockError(Exception):
    """Исключение выбрасывается, когда недостаточно блюд на витрине."""
    pass

def deduct_inventory_from_order(order: Order):
    """
    Списання порцій з вітрини для конкретного замовлення.
    Викликається ПРИ СТВОРЕННІ замовлення (резервування).
    """
    items = order.items.select_related('dish', 'combo').all()
    
    for item in items:
        if item.dish:
            inventory = Inventory.objects.select_for_update().filter(
                shift=order.shift, 
                dish=item.dish
            ).first()
            
            if not inventory or inventory.quantity < item.quantity:
                raise OutOfStockError(f"Недостатньо порцій для страви {item.dish.name}.")
            
            inventory.quantity = F('quantity') - item.quantity
            inventory.save()
        
        elif item.combo:
            for combo_dish in item.combo.dishes.all():
                inventory = Inventory.objects.select_for_update().filter(
                    shift=order.shift, 
                    dish=combo_dish
                ).first()
                
                if not inventory or inventory.quantity < item.quantity:
                    raise OutOfStockError(f"Недостатньо порцій {combo_dish.name} для комбо {item.combo.name}.")
                
                inventory.quantity = F('quantity') - item.quantity
                inventory.save()

def mark_order_as_paid(order: Order) -> Order:
    """
    Фіксація оплати замовлення.
    Тепер ТІЛЬКИ змінює статус, бо списання відбувається при створенні.
    """
    with transaction.atomic():
        locked_order = Order.objects.select_for_update().get(id=order.id)
        
        if locked_order.status == 'paid':
            return locked_order
            
        locked_order.status = 'paid'
        locked_order.save()
        
        return locked_order
