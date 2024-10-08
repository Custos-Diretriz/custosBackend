from django.db import models
import uuid

class LegalAgreement(models.Model):
    content = models.TextField()
    email = models.EmailField(null=True)
    access_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    agreement_id = models.IntegerField(null=True)
    agreementType = models.CharField(max_length=300, null=True)

    # First party details
    first_party_address = models.CharField(max_length=100)
    first_party_valid_id = models.ImageField(upload_to="valid_ids/", null=True, blank=True)  # Changed to ImageField
    first_party_country = models.CharField(max_length=300, null=True)
    first_party_id_type = models.CharField(max_length=300, null=True)
    first_party_fullname = models.CharField(max_length=1000, null=True)
    first_party_signature = models.FileField(
        upload_to="signatures/", null=True, blank=True
    )

    # Second party details
    second_party_address = models.CharField(max_length=100)
    second_party_valid_id = models.ImageField(upload_to="valid_ids/", null=True, blank=True)  # Changed to ImageField
    second_party_country = models.CharField(max_length=300, null=True)
    second_party_id_type = models.CharField(max_length=300, null=True)
    second_party_fullname = models.CharField(max_length=1000, null=True)
    second_party_signature = models.FileField(
        upload_to="signatures/", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Agreement by {self.content} with {self.second_party_address}"
