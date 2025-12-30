from rest_framework import serializers
from api.models import PrelationRequirement

class PrelationRequirementSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)
    prelation_id = serializers.IntegerField(source='prelation.id', read_only=True)
    prelation_order_name = serializers.CharField(source='prelation.order.name', read_only=True)

    class Meta:
        model = PrelationRequirement
        fields = ['id', 'prelation', 'prelation_id', 'prelation_order_name', 'text', 'logic_type', 'group', 'is_active']
