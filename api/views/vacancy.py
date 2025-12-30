from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import models
from api.models import EducationalInstitution, Vacancy, Phase, Modality, Level, CurricularArea
from api.serializers.vacancy import (
    EducationalInstitutionSerializer,
    VacancySerializer,
    VacancyBulkCreateSerializer
)
from api.functions.pagination import StandardResultsSetPagination
import pandas as pd
import io


class EducationalInstitutionViewSet(viewsets.ModelViewSet):
    queryset = EducationalInstitution.objects.all()
    serializer_class = EducationalInstitutionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Vacancy.objects.all().select_related(
            'phase', 'educational_institution', 'curricular_area',
            'educational_institution__modality', 'educational_institution__level'
        )
        
        # Filtrar por fase si se proporciona
        phase_id = self.request.query_params.get('phase', None)
        if phase_id:
            queryset = queryset.filter(phase_id=phase_id)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='preview')
    def preview(self, request):
        """
        Previsualizar vacantes desde Excel antes de cargar
        """
        try:
            file = request.FILES.get('file')
            phase_id = request.data.get('phase_id')
            
            if not file:
                return Response(
                    {'error': 'No se proporcionó ningún archivo'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not phase_id:
                return Response(
                    {'error': 'No se proporcionó el ID de la fase'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Leer archivo Excel
            df = pd.read_excel(file)
            
            # Validar columnas requeridas
            required_columns = ['ie_code', 'ie_name', 'modality', 'level', 'nexus_code', 'position', 'vacancy_type', 'vacancy_reason']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response(
                    {'error': f'Faltan columnas requeridas: {", ".join(missing_columns)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar cada fila
            preview_data = []
            errors = []
            
            for idx, row in df.iterrows():
                row_num = idx + 2  # +2 porque Excel empieza en 1 y tiene header
                row_errors = []
                
                # Validar modalidad
                modality = Modality.objects.filter(
                    models.Q(abbreviature__iexact=str(row['modality'])) |
                    models.Q(name__iexact=str(row['modality']))
                ).first()
                if not modality:
                    row_errors.append(f"Modalidad '{row['modality']}' no encontrada")
                
                # Validar nivel
                level = Level.objects.filter(name__iexact=str(row['level'])).first()
                if not level:
                    row_errors.append(f"Nivel '{row['level']}' no encontrado")
                
                # Validar área curricular si existe
                area_name = row.get('curricular_area')
                curricular_area_valid = True
                if area_name and not (isinstance(area_name, float) and pd.isna(area_name)):
                    area = CurricularArea.objects.filter(name__iexact=str(area_name)).first()
                    if not area:
                        row_errors.append(f"Área curricular '{area_name}' no encontrada")
                        curricular_area_valid = False
                
                preview_data.append({
                    'row': row_num,
                    'ie_code': str(row['ie_code']) if not pd.isna(row['ie_code']) else '',
                    'ie_name': str(row['ie_name']) if not pd.isna(row['ie_name']) else '',
                    'modality': str(row['modality']) if not pd.isna(row['modality']) else '',
                    'level': str(row['level']) if not pd.isna(row['level']) else '',
                    'nexus_code': str(row['nexus_code']) if not pd.isna(row['nexus_code']) else '',
                    'position': str(row['position']) if not pd.isna(row['position']) else '',
                    'vacancy_type': str(row['vacancy_type']) if not pd.isna(row['vacancy_type']) else '',
                    'vacancy_reason': str(row['vacancy_reason']) if not pd.isna(row['vacancy_reason']) else '',
                    'curricular_area': str(area_name) if area_name and not pd.isna(area_name) else None,
                    'errors': row_errors,
                    'valid': len(row_errors) == 0
                })
                
                if row_errors:
                    errors.append({
                        'row': row_num,
                        'errors': row_errors
                    })
            
            valid_count = sum(1 for item in preview_data if item['valid'])
            invalid_count = len(preview_data) - valid_count
            
            return Response({
                'total': len(preview_data),
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'preview': preview_data,
                'errors': errors
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error procesando el archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request):
        """
        Subir vacantes masivamente desde Excel
        Formato esperado en el Excel:
        - ie_code: Código modular de la IE
        - ie_name: Nombre de la IE
        - modality: Modalidad (EBR, EBA, etc)
        - level: Nivel (Inicial, Primaria, Secundaria)
        - nexus_code: Código Nexus
        - position: Cargo (DOCENTE, AUXILIAR)
        - vacancy_type: Tipo (ORGANICA, EVENTUAL)
        - vacancy_reason: Motivo (LICENCIA, DESTAQUE, etc)
        - curricular_area: Área Curricular (opcional)
        """
        try:
            file = request.FILES.get('file')
            phase_id = request.data.get('phase_id')
            
            if not file:
                return Response(
                    {'error': 'No se proporcionó ningún archivo'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not phase_id:
                return Response(
                    {'error': 'No se proporcionó el ID de la fase'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que la fase existe
            try:
                phase = Phase.objects.get(id=phase_id)
            except Phase.DoesNotExist:
                return Response(
                    {'error': 'La fase especificada no existe'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Leer archivo Excel
            df = pd.read_excel(file)
            
            # Validar columnas requeridas
            required_columns = ['ie_code', 'ie_name', 'modality', 'level', 'nexus_code', 'position', 'vacancy_type', 'vacancy_reason']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response(
                    {'error': f'Faltan columnas requeridas: {", ".join(missing_columns)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Convertir DataFrame a lista de diccionarios
            vacancies_data = df.to_dict('records')
            
            # Usar el serializer de bulk create
            serializer = VacancyBulkCreateSerializer(data={
                'phase_id': phase_id,
                'vacancies': vacancies_data
            })
            
            if serializer.is_valid():
                result = serializer.save()
                
                return Response({
                    'message': f'Se crearon {result["created_count"]} vacantes exitosamente',
                    'created_count': result['created_count'],
                    'error_count': result['error_count'],
                    'errors': result['errors']
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {'error': f'Error procesando el archivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='export-template')
    def export_template(self, request):
        """
        Descargar plantilla Excel para subir vacantes
        """
        from django.http import HttpResponse
        
        # Crear DataFrame con la estructura
        df = pd.DataFrame(columns=[
            'ie_code', 'ie_name', 'modality', 'level', 'nexus_code',
            'position', 'vacancy_type', 'vacancy_reason', 'curricular_area'
        ])
        
        # Agregar una fila de ejemplo
        df.loc[0] = [
            '0123456',
            'I.E. María Auxiliadora',
            'EBR',
            'Secundaria',
            'NEX001',
            'DOCENTE',
            'ORGANICA',
            'LICENCIA',
            'Matemática'
        ]
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Vacantes')
        
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=plantilla_vacantes.xlsx'
        
        return response
