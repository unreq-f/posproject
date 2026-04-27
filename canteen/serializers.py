from rest_framework import serializers
from .models import Shift, WriteOff

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'
        read_only_fields = ['status', 'end_time']

class WriteOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriteOff
        fields = '__all__'
        read_only_fields = ['created_at']
