from django.db import models

class Dish(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ComboMeal(models.Model):
    name = models.CharField(max_length=255)
    dishes = models.ManyToManyField(Dish, related_name='combos')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Menu(models.Model):
    shift = models.ForeignKey('canteen.Shift', on_delete=models.CASCADE, related_name='menus')
    dishes = models.ManyToManyField(Dish, blank=True)
    combos = models.ManyToManyField(ComboMeal, blank=True)

    def __str__(self):
        return f"Меню для смены {self.shift.id}"

class Inventory(models.Model):
    shift = models.ForeignKey('canteen.Shift', on_delete=models.CASCADE, related_name='inventory')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('shift', 'dish')

    def __str__(self):
        return f"{self.dish.name} - {self.quantity} шт. (Смена {self.shift.id})"
