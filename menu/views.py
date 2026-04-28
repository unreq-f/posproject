from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Dish, ComboMeal, Inventory
from canteen.models import Shift
from .serializers import DishSerializer, ComboMealSerializer, InventorySerializer, AddInventorySerializer
from .services import add_inventory
from django.shortcuts import get_object_or_404

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ComboMealViewSet(viewsets.ModelViewSet):
    queryset = ComboMeal.objects.all()
    serializer_class = ComboMealSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'])
    def add_to_showcase(self, request):
        """
        Custom action to add prepared dishes to the showcase for a given shift.
        Payload expects: shift_id, dish_id, quantity
        """
        shift_id = request.data.get('shift_id')
        shift = get_object_or_404(Shift, id=shift_id)
        
        serializer = AddInventorySerializer(data=request.data)
        if serializer.is_valid():
            dish = get_object_or_404(Dish, id=serializer.validated_data['dish_id'])
            try:
                inventory = add_inventory(shift, dish, serializer.validated_data['quantity'])
                inv_serializer = self.get_serializer(inventory)
                return Response(inv_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
