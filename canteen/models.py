from django.db import models
from django.conf import settings

class Shift(models.Model):
    STATUS_CHOICES = (
        ('open', 'Открыта'),
        ('closed', 'Закрыта'),
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    initial_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Розмінний фонд")
    responsible_staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shifts')

    def __str__(self):
        return f"Смена {self.id} ({self.get_status_display()})"

class WriteOff(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='writeoffs')
    dish = models.ForeignKey('menu.Dish', on_delete=models.CASCADE, related_name='writeoffs')
    quantity = models.IntegerField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Списание {self.quantity} шт. {self.dish.name} (Смена {self.shift.id})"
