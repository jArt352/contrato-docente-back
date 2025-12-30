from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from api.models import Prelation
from api.serializers import PrelationSerializer
from api.functions.pagination import StandardResultsSetPagination


class PrelationViewSet(viewsets.ModelViewSet):
    queryset = Prelation.objects.select_related(
        'modality', 'curricular_area', 'order'
    ).prefetch_related('level', 'requirements').order_by('id')
    serializer_class = PrelationSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """Permitir lectura sin autenticación, pero requerir admin para modificaciones"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """
        Validar que no se pueda eliminar una prelación si hay prelaciones posteriores.
        Solo se permite eliminar de atrás hacia adelante manteniendo el orden.
        """
        instance = self.get_object()
        
        # Obtener todas las prelaciones con la misma modalidad y área curricular
        same_group_prelations = Prelation.objects.filter(
            modality=instance.modality,
            curricular_area=instance.curricular_area
        ).select_related('order').order_by('order__id')
        
        # Obtener los órdenes únicos ordenados
        orders = list(same_group_prelations.values_list('order__id', flat=True).distinct())
        
        if not orders:
            # Si no hay otros órdenes, permitir eliminar
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        # Verificar si es el último orden (el más alto)
        max_order_id = max(orders)
        
        if instance.order.id != max_order_id:
            # Obtener el nombre del orden actual y los posteriores
            posterior_prelations = same_group_prelations.filter(
                order__id__gt=instance.order.id
            )
            posterior_orders = ', '.join(set([p.order.name for p in posterior_prelations]))
            
            raise ValidationError({
                'error': f'No se puede eliminar la prelación "{instance.order.name}" porque existen prelaciones posteriores: {posterior_orders}. '
                         f'Debe eliminar las prelaciones en orden inverso (de atrás hacia adelante).'
            })
        
        # Si llegamos aquí, es seguro eliminar
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
