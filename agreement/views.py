from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import LegalAgreement
from .serializers import LegalAgreementSerializer
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from django.core.exceptions import PermissionDenied
import os, uuid
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile



class LegalAgreementViewSet(viewsets.ModelViewSet):
    serializer_class = LegalAgreementSerializer
    parser_classes = [MultiPartParser, FormParser] 


    def get_queryset(self):
        return LegalAgreement.objects.none() 

    def get_object(self):
        agreement_id = self.kwargs.get('pk')
        try:
            return LegalAgreement.objects.get(id=agreement_id)
        except LegalAgreement.DoesNotExist:
            raise PermissionDenied("Agreement not found.")

    def perform_create(self, serializer):
        # Unique naming for files
        instance = serializer.save()
        self.rename_uploaded_files(instance)
        access_token = instance.access_token
        
        if instance.email:
            self.send_access_token_email(instance.email, access_token)
        
        response_data = {
            "agreement": LegalAgreementSerializer(instance).data,
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
        
        if 'access_token' in request.data:
            # Update through access token route
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        else:
            # Update through ID route
            second_party_fields = [
                'second_party_valid_id',
                'second_party_country',
                'second_party_id_type',
                'second_party_signature',
                'second_party_fullname',
            ]
            for field in second_party_fields:
                if field in request.data:
                    setattr(instance, field, request.data[field])
            instance.save()
            serializer = self.get_serializer(instance)
            self.rename_uploaded_files(instance)  # Rename uploaded files after update

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'address',
                openapi.IN_QUERY,
                description="Address of the party",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_party(self, request, *args, **kwargs):
        address = request.query_params.get('address')

        if address:
            agreements = LegalAgreement.objects.filter(
                first_party_address=address
            ) | LegalAgreement.objects.filter(
                second_party_address=address
            )
        else:
            return Response({"detail": "Query parameter 'address' is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(agreements, many=True)
        data = serializer.data

        for item in data:
            agreement = LegalAgreement.objects.get(id=item['id'])
            if agreement.first_party_address == address:
                item['access_token'] = str(agreement.access_token)
            else:
                item['access_token'] = None

        return Response(data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'access_token',
                openapi.IN_QUERY,
                description="Access token",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='access_token')
    def get_by_access_token(self, request, *args, **kwargs):
        access_token = request.query_params.get('access_token')
        try:
            agreement = LegalAgreement.objects.get(access_token=access_token)
        except LegalAgreement.DoesNotExist:
            return Response({"detail": "Invalid access token."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(agreement)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data.pop('access_token', None)
        return Response(data)

    @action(detail=False, methods=['patch', 'put'], url_path='access_token_update')
    def update_by_access_token(self, request, *args, **kwargs):
        access_token = request.query_params.get('access_token')
        try:
            instance = LegalAgreement.objects.get(access_token=access_token)
        except LegalAgreement.DoesNotExist:
            return Response({"detail": "Invalid access token."}, status=status.HTTP_400_BAD_REQUEST)
        
        restricted_fields = [
            'second_party_valid_id',
            'second_party_country',
            'second_party_id_type',
            'second_party_signature',
        ]
        data = request.data.copy()
        for field in restricted_fields:
            data.pop(field, None)
        
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.rename_uploaded_files(instance)  # Rename uploaded files after update
        
        return Response(serializer.data)

    def rename_uploaded_files(self, instance):
        """
        Function to rename uploaded files with unique names using UUID.
        """
        if instance.first_party_valid_id:
            self.rename_file(instance.first_party_valid_id)
        if instance.second_party_valid_id:
            self.rename_file(instance.second_party_valid_id)
        if instance.first_party_signature:
            self.rename_file(instance.first_party_signature)
        if instance.second_party_signature:
            self.rename_file(instance.second_party_signature)



    def rename_file(self, file_field):
        if file_field and os.path.isfile(file_field.path):
            base, extension = os.path.splitext(file_field.name)
            new_name = f"{uuid.uuid4()}{extension}"
            new_path = os.path.join(os.path.dirname(file_field.path), new_name)

            # Read the content of the file
            with open(file_field.path, 'rb') as file:
                file_content = file.read()

            # Delete the old file after reading its content
            os.remove(file_field.path)
            # Save the file with the new name and content
            file_field.save(new_name, ContentFile(file_content))

