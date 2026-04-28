from rest_framework import serializers
from .models import Shift, WriteOff

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'
        read_only_fields = ['status', 'end_time']

    def validate(self, data):
        # Забороняємо відкривати нову зміну, якщо існує незакрита
        if not self.instance:  # Тільки при створенні (POST)
            open_shift = Shift.objects.filter(status='open').exists()
            if open_shift:
                raise serializers.ValidationError(
                    "Неможливо відкрити нову зміну: попередня зміна ще не закрита."
                )
        return data

class WriteOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriteOff
        fields = '__all__'
        read_only_fields = ['created_at']
