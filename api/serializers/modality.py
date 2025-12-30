from rest_framework import serializers
from api.models import Modality


class ModalitySerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, initial=True)

    class Meta:
        model = Modality
        fields = ['id', 'name', 'abbreviature', 'is_active']
