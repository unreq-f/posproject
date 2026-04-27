import pytest
from canteen.models import Shift, WriteOff
from menu.models import Dish, Inventory
from canteen.services import close_shift
from users.models import User

@pytest.fixture
def user(db):
    return User.objects.create(username="testuser", role="staff")

@pytest.fixture
def shift(db, user):
    return Shift.objects.create(responsible_staff=user)

@pytest.fixture
def dish(db):
    return Dish.objects.create(name="Борщ", category="Первое", price=60.00)

@pytest.mark.django_db(transaction=True)
def test_close_shift_writeoff_logic(shift, dish):
    # Оставляем на витрине 10 порций борща
    inventory = Inventory.objects.create(shift=shift, dish=dish, quantity=10)
    
    # Закрываем смену
    closed_shift = close_shift(shift)
    
    # Проверяем, что смена закрылась
    assert closed_shift.status == 'closed'
    assert closed_shift.end_time is not None
    
    # Проверяем, что остаток на витрине обнулился
    inventory.refresh_from_db()
    assert inventory.quantity == 0
    
    # Проверяем, что создалась запись о списании (WriteOff) с правильным количеством
    write_offs = WriteOff.objects.filter(shift=shift)
    assert write_offs.count() == 1
    assert write_offs.first().quantity == 10
    assert write_offs.first().dish == dish
    assert write_offs.first().reason == "Кінець зміни"
