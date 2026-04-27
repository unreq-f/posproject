from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Shift, WriteOff
from .serializers import ShiftSerializer, WriteOffSerializer
from .services import close_shift

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        shift = self.get_object()
        try:
            closed_shift = close_shift(shift)
            serializer = self.get_serializer(closed_shift)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WriteOffViewSet(viewsets.ModelViewSet):
    queryset = WriteOff.objects.all()
    serializer_class = WriteOffSerializer
