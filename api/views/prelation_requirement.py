from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from api.models import PrelationRequirement
from api.serializers.prelation_requirement import PrelationRequirementSerializer

class PrelationRequirementViewSet(viewsets.ModelViewSet):
    queryset = PrelationRequirement.objects.select_related('prelation').all()
    serializer_class = PrelationRequirementSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if is_many:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            headers = self.get_success_headers(serializer.data)
            from rest_framework.response import Response
            return Response(serializer.data, status=201, headers=headers)
        return super().create(request, *args, **kwargs)

    def perform_bulk_create(self, serializer):
        self.get_queryset().model.objects.bulk_create([
            self.get_queryset().model(**item) for item in serializer.validated_data
        ])
