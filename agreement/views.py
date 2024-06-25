from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import LegalAgreement
from .serializers import LegalAgreementSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied

class LegalAgreementViewSet(viewsets.ModelViewSet):
    serializer_class = LegalAgreementSerializer

    def get_queryset(self):
        return LegalAgreement.objects.none()  # Disable the list action

    def get_object(self):
        access_token = self.kwargs.get('access_token')
        if not access_token:
            raise PermissionDenied("Access token is required.")
        
        try:
            return LegalAgreement.objects.get(access_token=access_token)
        except LegalAgreement.DoesNotExist:
            raise PermissionDenied("Invalid access token.")

    def perform_create(self, serializer):
        agreement = serializer.save()
        access_token = agreement.access_token
        
        if agreement.email:
            self.send_access_token_email(agreement.email, access_token)
        
        response_data = {
            "agreement": LegalAgreementSerializer(agreement).data,
            "access_token": access_token,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.perform_create(serializer)

    def send_access_token_email(self, email, access_token):
        send_mail(
            'Your Legal Agreement Access Token',
            f'Your access token for the legal agreement is: {access_token}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def by_party(self, request, *args, **kwargs):
        first_party_address = request.query_params.get('first_party_address')
        second_party_address = request.query_params.get('second_party_address')

        if first_party_address:
            agreements = LegalAgreement.objects.filter(first_party_address=first_party_address)
        elif second_party_address:
            agreements = LegalAgreement.objects.filter(second_party_address=second_party_address)
        else:
            return Response({"detail": "Query parameter 'first_party_address' or 'second_party_address' is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(agreements, many=True)
        return Response(serializer.data)
