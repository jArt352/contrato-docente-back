from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from api.models import CurricularArea
from api.serializers import CurricularAreaSerializer


class CurricularAreaViewSet(viewsets.ModelViewSet):
    queryset = CurricularArea.objects.all()
    serializer_class = CurricularAreaSerializer

    def get_permissions(self):
        """Permitir lectura sin autenticación, pero requerir admin para modificaciones"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
