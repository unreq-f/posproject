from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .services import mark_order_as_paid, OutOfStockError

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        try:
            paid_order = mark_order_as_paid(order)
            serializer = self.get_serializer(paid_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OutOfStockError as e:
            return Response({'detail': str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
