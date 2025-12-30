from rest_framework import serializers
from api.models import PrelationOrder


class PrelationOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrelationOrder
        fields = ['id', 'name']
