import pytest
from canteen.models import Shift
from menu.models import Dish, Inventory
from menu.services import add_inventory
from users.models import User

@pytest.fixture
def user(db):
    return User.objects.create(username="testuser", role="staff")

@pytest.fixture
def shift(db, user):
    return Shift.objects.create(responsible_staff=user)

@pytest.fixture
def dish(db):
    return Dish.objects.create(name="Пюре", category="Гарнир", price=40.00)

@pytest.mark.django_db(transaction=True)
def test_add_inventory_creates_new(shift, dish):
    # Добавляем 50 порций
    inventory = add_inventory(shift, dish, 50)
    
    assert inventory.quantity == 50
    assert inventory.shift == shift
    assert inventory.dish == dish

@pytest.mark.django_db(transaction=True)
def test_add_inventory_increments_existing(shift, dish):
    # Добавляем 50 порций
    add_inventory(shift, dish, 50)
    # Позже в тот же день доготовили еще 30
    inventory = add_inventory(shift, dish, 30)
    
    # Должно получиться 80
    assert inventory.quantity == 80
