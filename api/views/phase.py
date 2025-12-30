from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api.models import Phase, PhaseStage, PhaseAssignment
from api.serializers.phase import (
    PhaseSerializer, 
    PhaseCreateSerializer, 
    PhaseStageSerializer, 
    PhaseAssignmentSerializer
)
from api.functions.pagination import StandardResultsSetPagination


class PhaseViewSet(viewsets.ModelViewSet):
    queryset = Phase.objects.prefetch_related('stages', 'assignments').all()
    serializer_class = PhaseSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PhaseCreateSerializer
        return PhaseSerializer
    
    @action(detail=True, methods=['post'])
    def add_assignment(self, request, pk=None):
        """
        Agregar una nueva adjudicación a una fase existente
        """
        phase = self.get_object()
        serializer = PhaseAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(phase=phase)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_stage(self, request, pk=None):
        """
        Actualizar una etapa específica de la fase
        """
        phase = self.get_object()
        stage_id = request.data.get('stage_id')
        
        if not stage_id:
            return Response(
                {'error': 'Se requiere stage_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stage = PhaseStage.objects.get(id=stage_id, phase=phase)
        except PhaseStage.DoesNotExist:
            return Response(
                {'error': 'Etapa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PhaseStageSerializer(stage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhaseStageViewSet(viewsets.ModelViewSet):
    queryset = PhaseStage.objects.select_related('phase').all()
    serializer_class = PhaseStageSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        phase_id = self.request.query_params.get('phase', None)
        if phase_id:
            queryset = queryset.filter(phase_id=phase_id)
        return queryset


class PhaseAssignmentViewSet(viewsets.ModelViewSet):
    queryset = PhaseAssignment.objects.select_related(
        'phase', 'modality', 'level', 'curricular_area'
    ).all()
    serializer_class = PhaseAssignmentSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        phase_id = self.request.query_params.get('phase', None)
        if phase_id:
            queryset = queryset.filter(phase_id=phase_id)
        return queryset
