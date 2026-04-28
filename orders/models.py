from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('paid', 'Оплачен'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    )
    ORDER_TYPE_CHOICES = (
        ('online', 'Онлайн'),
        ('offline', 'Офлайн (Касса)'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('card', 'Карта'),
        ('cash', 'Наличные'),
        ('voucher', 'Ваучер (Талон)'),
    )

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    shift = models.ForeignKey('canteen.Shift', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='offline')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    pickup_time = models.CharField(max_length=50, blank=True, null=True, verbose_name="Час отримання (Time-slot)")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.id} ({self.get_status_display()})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey('menu.Dish', on_delete=models.SET_NULL, null=True, blank=True)
    combo = models.ForeignKey('menu.ComboMeal', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price_fixed = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        item_name = self.dish.name if self.dish else (self.combo.name if self.combo else "Удаленный товар")
        return f"{self.quantity} x {item_name} (Заказ {self.order.id})"
