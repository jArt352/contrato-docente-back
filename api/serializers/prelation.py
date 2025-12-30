from rest_framework import serializers
from api.models import Prelation, Level
from .prelation_requirement import PrelationRequirementSerializer


class PrelationSerializer(serializers.ModelSerializer):
    requirements = PrelationRequirementSerializer(many=True, read_only=True)
    modality_name = serializers.CharField(source='modality.name', read_only=True)
    level = serializers.PrimaryKeyRelatedField(many=True, queryset=Level.objects.all())
    level_names = serializers.SerializerMethodField()
    curricular_area_name = serializers.CharField(source='curricular_area.name', read_only=True)
    order_name = serializers.CharField(source='order.name', read_only=True)
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = Prelation
        fields = [
            'id', 'modality', 'modality_name', 'level', 'level_names',
            'curricular_area', 'curricular_area_name', 'order', 'order_name',
            'description', 'requirements', 'is_active'
        ]

    def create(self, validated_data):
        levels = validated_data.pop('level', [])
        prelation = Prelation.objects.create(**validated_data)
        prelation.level.set(levels)
        return prelation

    def update(self, instance, validated_data):
        levels = validated_data.pop('level', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if levels is not None:
            instance.level.set(levels)
        return instance

    def get_level_names(self, obj):
        return [level.name for level in obj.level.all()]
