import pytest
from django.db import IntegrityError
from canteen.models import Shift
from menu.models import Dish, Inventory
from orders.models import Order, OrderItem
from orders.services import mark_order_as_paid, OutOfStockError
from users.models import User

@pytest.fixture
def user(db):
    return User.objects.create(username="testuser", role="staff")

@pytest.fixture
def shift(db, user):
    return Shift.objects.create(responsible_staff=user)

@pytest.fixture
def dish_soup(db):
    return Dish.objects.create(name="Суп", category="Первое", price=50.00)

@pytest.mark.django_db(transaction=True)
def test_mark_order_as_paid_success(shift, dish_soup):
    # Добавляем 5 супов на витрину
    inventory = Inventory.objects.create(shift=shift, dish=dish_soup, quantity=5)
    
    # Создаем заказ на 2 супа
    order = Order.objects.create(shift=shift, payment_method='cash', total_amount=100.00)
    OrderItem.objects.create(order=order, dish=dish_soup, quantity=2, price_fixed=50.00)
    
    # Оплачиваем заказ
    paid_order = mark_order_as_paid(order)
    
    # Проверяем, что статус изменился
    assert paid_order.status == 'paid'
    
    # Проверяем, что остаток уменьшился до 3
    inventory.refresh_from_db()
    assert inventory.quantity == 3

@pytest.mark.django_db(transaction=True)
def test_mark_order_as_paid_out_of_stock_rollback(shift, dish_soup):
    # Добавляем ТОЛЬКО 2 супа на витрину
    inventory = Inventory.objects.create(shift=shift, dish=dish_soup, quantity=2)
    
    # Создаем заказ на 3 супа (больше, чем есть в наличии)
    order = Order.objects.create(shift=shift, payment_method='cash', total_amount=150.00)
    OrderItem.objects.create(order=order, dish=dish_soup, quantity=3, price_fixed=50.00)
    
    # Попытка оплатить заказ должна вызвать ошибку OutOfStockError
    with pytest.raises(OutOfStockError):
        mark_order_as_paid(order)
    
    # Проверяем, что статус заказа НЕ изменился на paid
    order.refresh_from_db()
    assert order.status == 'pending'
    
    # Проверяем, что остаток на витрине НЕ уменьшился (транзакция откатилась)
    inventory.refresh_from_db()
    assert inventory.quantity == 2
