from django.db import transaction
from django.utils import timezone
from .models import Shift, WriteOff
from menu.models import Inventory

def close_shift(shift: Shift) -> Shift:
    """
    Закрытие смены: 
    Находит все остатки (Inventory) для данной смены с количеством > 0, 
    создает для них записи о списании (WriteOff) с причиной "Кінець зміни", 
    обнуляет остатки на витрине и закрывает смену.
    """
    with transaction.atomic():
        locked_shift = Shift.objects.select_for_update().get(id=shift.id)
        
        if locked_shift.status == 'closed':
            return locked_shift
            
        # Находим все нераспроданные позиции на витрине
        inventories = Inventory.objects.select_for_update().filter(
            shift=locked_shift,
            quantity__gt=0
        )
        
        for inv in inventories:
            # Списываем остаток
            WriteOff.objects.create(
                shift=locked_shift,
                dish=inv.dish,
                quantity=inv.quantity,
                reason="Кінець зміни"
            )
            # Обнуляем витрину
            inv.quantity = 0
            inv.save()
            
        # Обновляем статус смены и время закрытия
        locked_shift.status = 'closed'
        locked_shift.end_time = timezone.now()
        locked_shift.save()
        
        return locked_shift
