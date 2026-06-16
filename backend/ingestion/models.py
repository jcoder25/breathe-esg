from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class IngestionBatch(models.Model):
    SOURCE_TYPES = [
        ('sap', 'SAP Fuel & Procurement'),
        ('utility', 'Utility Electricity'),
        ('travel', 'Corporate Travel'),
    ]
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='batches')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    row_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.client.name} - {self.source_type} - {self.uploaded_at.date()}"


class RawRecord(models.Model):
    PARSE_STATUS = [
        ('ok', 'Parsed OK'),
        ('error', 'Parse Error'),
    ]

    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE, related_name='raw_records')
    row_number = models.IntegerField()
    raw_data = models.JSONField()
    parse_status = models.CharField(max_length=10, choices=PARSE_STATUS, default='ok')
    parse_error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Row {self.row_number} - Batch {self.batch.id}"


class EmissionRecord(models.Model):
    SCOPE_CHOICES = [
        (1, 'Scope 1 - Direct'),
        (2, 'Scope 2 - Electricity'),
        (3, 'Scope 3 - Travel'),
    ]
    REVIEW_STATUS = [
        ('pending', 'Pending Review'),
        ('flagged', 'Flagged'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('locked', 'Locked'),
    ]
    CATEGORY_CHOICES = [
        ('fuel_combustion', 'Fuel Combustion'),
        ('purchased_electricity', 'Purchased Electricity'),
        ('business_travel_air', 'Business Travel - Air'),
        ('business_travel_hotel', 'Business Travel - Hotel'),
        ('business_travel_ground', 'Business Travel - Ground'),
    ]

    # Source tracking
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='emissions')
    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE, related_name='emission_records')
    raw_record = models.OneToOneField(RawRecord, on_delete=models.CASCADE, related_name='emission')

    # Classification
    scope = models.IntegerField(choices=SCOPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    # Activity data (original values before normalization)
    activity_value = models.FloatField()
    activity_unit = models.CharField(max_length=50)

    # Normalized emission
    normalized_kgco2e = models.FloatField()
    emission_factor = models.FloatField()
    emission_factor_source = models.CharField(max_length=255)

    # Time period
    period_start = models.DateField()
    period_end = models.DateField()

    # Description
    description = models.TextField(blank=True)

    # Review workflow
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_emissions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.name} - {self.category} - {self.period_start}"


class Flag(models.Model):
    FLAG_REASONS = [
        ('high_value', 'Unusually High Value'),
        ('missing_data', 'Missing Data'),
        ('unit_mismatch', 'Unit Mismatch'),
        ('duplicate', 'Possible Duplicate'),
        ('manual', 'Manually Flagged'),
    ]

    emission_record = models.ForeignKey(EmissionRecord, on_delete=models.CASCADE, related_name='flags')
    reason = models.CharField(max_length=50, choices=FLAG_REASONS)
    detail = models.TextField(blank=True)
    auto_flagged = models.BooleanField(default=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Flag: {self.reason} on record {self.emission_record.id}"


class AuditLog(models.Model):
    emission_record = models.ForeignKey(EmissionRecord, on_delete=models.CASCADE, related_name='audit_logs')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField()
    new_value = models.TextField()

    def __str__(self):
        return f"AuditLog: {self.field_name} changed at {self.changed_at}"
    
