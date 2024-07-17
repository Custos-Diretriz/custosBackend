from rest_framework import serializers
from .models import LegalAgreement

class LegalAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalAgreement
        fields = '__all__'
        read_only_fields = ['access_token', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_at'] = instance.created_at
        return representation
