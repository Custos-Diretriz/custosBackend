from rest_framework import serializers
from .models import LegalAgreement

class LegalAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalAgreement
        fields = '__all__'
