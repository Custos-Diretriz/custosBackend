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

        # Include full file URLs in the representation (if using Django's MEDIA_URL)
        request = self.context.get('request')
        if instance.first_party_valid_id:
            representation['first_party_valid_id'] = request.build_absolute_uri(instance.first_party_valid_id.url) if request else instance.first_party_valid_id.url
        if instance.second_party_valid_id:
            representation['second_party_valid_id'] = request.build_absolute_uri(instance.second_party_valid_id.url) if request else instance.second_party_valid_id.url
        if instance.first_party_signature:
            representation['first_party_signature'] = request.build_absolute_uri(instance.first_party_signature.url) if request else instance.first_party_signature.url
        if instance.second_party_signature:
            representation['second_party_signature'] = request.build_absolute_uri(instance.second_party_signature.url) if request else instance.second_party_signature.url

        return representation
