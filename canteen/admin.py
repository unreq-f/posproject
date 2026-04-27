from django.contrib import admin
from .models import Shift, WriteOff

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'start_time', 'end_time', 'responsible_staff')
    list_filter = ('status',)

@admin.register(WriteOff)
class WriteOffAdmin(admin.ModelAdmin):
    list_display = ('id', 'shift', 'dish', 'quantity', 'created_at')
    list_filter = ('shift', 'dish')
