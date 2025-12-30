from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from api.models import Modality
from api.serializers import ModalitySerializer


class ModalityViewSet(viewsets.ModelViewSet):
    queryset = Modality.objects.all()
    serializer_class = ModalitySerializer

    def get_permissions(self):
        """Permitir lectura sin autenticación, pero requerir admin para modificaciones"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
