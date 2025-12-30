from rest_framework import serializers
from api.models import CurricularArea


class CurricularAreaSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)
    
    class Meta:
        model = CurricularArea
        fields = ['id', 'name', 'is_active']
