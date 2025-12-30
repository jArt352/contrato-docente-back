from rest_framework import serializers
from api.models import Level


class LevelSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)
    
    class Meta:
        model = Level
        fields = ['id', 'name', 'is_active']
