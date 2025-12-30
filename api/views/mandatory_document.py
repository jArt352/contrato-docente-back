from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
import os

from api.models import MandatoryDocument
from api.serializers.mandatory_document import MandatoryDocumentSerializer

class MandatoryDocumentViewSet(viewsets.ModelViewSet):
    queryset = MandatoryDocument.objects.all()
    serializer_class = MandatoryDocumentSerializer

    def get_permissions(self):
        """Permitir lectura sin autenticación, pero requerir admin para modificaciones"""
        if self.action in ['list', 'retrieve', 'available_files']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def available_files(self, request):
        """Lista los archivos PDF disponibles en la carpeta mandatory_documents"""
        mandatory_docs_path = os.path.join(settings.BASE_DIR, 'mandatory_documents')
        
        if not os.path.exists(mandatory_docs_path):
            return Response({'files': []})
        
        files = []
        for filename in os.listdir(mandatory_docs_path):
            if filename.endswith('.pdf'):
                # Extraer información del nombre del archivo
                # Formato esperado: ANEXO_8.pdf, ANEXO_9.pdf, etc.
                file_info = {
                    'filename': filename,
                    'name': filename.replace('.pdf', '').replace('_', ' '),
                    'url': f'{request.scheme}://{request.get_host()}/mandatory_documents/{filename}',
                    'size': os.path.getsize(os.path.join(mandatory_docs_path, filename))
                }
                files.append(file_info)
        
        # Ordenar por nombre de archivo
        files.sort(key=lambda x: x['filename'])
        
        return Response({'files': files})
