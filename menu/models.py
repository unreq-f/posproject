from django.db import models

class Dish(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight_info = models.CharField(max_length=50, blank=True, help_text="Наприклад: 300г, 1шт")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)

    def __str__(self):
        return self.name

class ComboMeal(models.Model):
    name = models.CharField(max_length=255)
    dishes = models.ManyToManyField(Dish, related_name='combos')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name



class Inventory(models.Model):
    shift = models.ForeignKey('canteen.Shift', on_delete=models.CASCADE, related_name='inventory')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('shift', 'dish')

    def __str__(self):
        return f"{self.dish.name} - {self.quantity} шт. (Зміна {self.shift.id})"

class Replenishment(models.Model):
    shift = models.ForeignKey('canteen.Shift', on_delete=models.CASCADE, related_name='replenishments')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"+{self.quantity} {self.dish.name} (Зміна {self.shift.id})"
