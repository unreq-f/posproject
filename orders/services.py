from django.db import transaction
from django.db.models import F
from .models import Order
from menu.models import Inventory

class OutOfStockError(Exception):
    """Исключение выбрасывается, когда недостаточно блюд на витрине."""
    pass

def mark_order_as_paid(order: Order) -> Order:
    """
    Продажа (Списание со склада):
    При переводе заказа в статус 'paid', сервис проверяет остатки и списывает их.
    Используется транзакция и блокировка строк для предотвращения состояния гонки (race condition).
    """
    with transaction.atomic():
        # Блокируем заказ от параллельных изменений
        locked_order = Order.objects.select_for_update().get(id=order.id)
        
        if locked_order.status == 'paid':
            return locked_order
            
        items = locked_order.items.select_related('dish', 'combo').all()
        
        for item in items:
            if item.dish:
                # Получаем и блокируем запись остатков
                inventory = Inventory.objects.select_for_update().filter(
                    shift=locked_order.shift, 
                    dish=item.dish
                ).first()
                
                if not inventory or inventory.quantity < item.quantity:
                    raise OutOfStockError(f"Недостаточно порций для блюда {item.dish.name}.")
                
                # Списываем остаток
                inventory.quantity = F('quantity') - item.quantity
                inventory.save()
            
            elif item.combo:
                # Для комбо списываем каждое блюдо, входящее в его состав
                combo_dishes = item.combo.dishes.all()
                for combo_dish in combo_dishes:
                    inventory = Inventory.objects.select_for_update().filter(
                        shift=locked_order.shift, 
                        dish=combo_dish
                    ).first()
                    
                    if not inventory or inventory.quantity < item.quantity:
                        raise OutOfStockError(f"Недостаточно порций {combo_dish.name} для комбо {item.combo.name}.")
                    
                    inventory.quantity = F('quantity') - item.quantity
                    inventory.save()
                    
        # Фиксируем успешную оплату
        locked_order.status = 'paid'
        locked_order.save()
        
        return locked_order
