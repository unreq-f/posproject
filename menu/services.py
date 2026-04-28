from django.db import transaction
from django.db.models import F
from .models import Inventory, Dish
from canteen.models import Shift

def add_inventory(shift: Shift, dish: Dish, quantity: int) -> Inventory:
    """
    Приход (Формирование витрины):
    Добавляет приготовленные порции блюда на витрину (Inventory) для текущей смены.
    Если запись для блюда уже существует, увеличивает количество.
    """
    if quantity <= 0:
        raise ValueError("Количество должно быть положительным")
        
    with transaction.atomic():
        inventory, created = Inventory.objects.select_for_update().get_or_create(
            shift=shift,
            dish=dish,
            defaults={'quantity': 0}
        )
        
        # Используем F() выражение для избежания состояния гонки при одновременном пополнении
        inventory.quantity = F('quantity') + quantity
        inventory.save()
        
        # Обновляем объект из БД, чтобы получить актуальное значение quantity после применения F()
        inventory.refresh_from_db()
        
        # ФІКСАЦІЯ В ІСТОРІЇ: створюємо запис про поповнення
        from .models import Replenishment
        Replenishment.objects.create(
            shift=shift,
            dish=dish,
            quantity=quantity
        )
        
        return inventory
