from rest_framework import serializers
from api.models import MandatoryDocument

class MandatoryDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MandatoryDocument
        fields = ['id', 'name', 'description', 'file']
